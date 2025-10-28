from flask import render_template, request, Blueprint, flash, redirect, url_for
from urllib.parse import unquote
from app.extensions import db
from app.utils.helpers import has_unlocked_exam
from app.blueprints.auth.routes import verify_jwt_token
from app.models import Lecture, LectureReview, ExamInfo, PointHistory

lecture_bp = Blueprint("lecture", __name__)

DEFAULT_EXAM_VIEW_PRICE = 5


# 포인트 관련
def add_point_event(user_id, delta, reason, ref_type=None, ref_id=None):
    event = PointHistory(user_id=user_id, delta=delta, reason=reason,
                         ref_type=ref_type, ref_id=ref_id)
    db.session.add(event)

def award_once(user_id, delta, reason, ref_type, ref_id):
    exists = PointHistory.query.filter_by(
        user_id=user_id, reason=reason, ref_type=ref_type, ref_id=ref_id
    ).first()
    if not exists:
        add_point_event(user_id, delta, reason, ref_type, ref_id)

def get_user_points(user_id) -> int:
    pts = db.session.query(db.func.coalesce(db.func.sum(PointHistory.delta), 0)).filter_by(user_id=user_id).scalar()
    return int(pts)


def get_current_user_id():
    token = request.cookies.get("auth_token")
    if token:
        return verify_jwt_token(token)
    return None


# 강의실 홈
@lecture_bp.route("/", methods=["GET"])
def lecture_home():
    q = (request.args.get("q") or "").strip()
    user_id = get_current_user_id()
    my_point = get_user_points(user_id) if user_id else 0

    query = LectureReview.query.join(Lecture).add_columns(
        LectureReview.r_id, LectureReview.lecture_id, LectureReview.semester,
        LectureReview.content, LectureReview.author, LectureReview.created_at,
        Lecture.name.label("lecture_name"), Lecture.professor
    )
    if q:
        like = f"%{q}%"
        query = query.filter((Lecture.name.like(like)) | (Lecture.professor.like(like)))
    rows = query.order_by(LectureReview.r_id.desc()).limit(20).all()

    reviews = []
    for row in rows:
        text = unquote(row.content) if "%" in row.content else row.content
        preview = (text[:140] + "...") if len(text) > 140 else text
        reviews.append({
            "r_id": row.r_id,
            "lecture_id": row.lecture_id,
            "lecture_name": row.lecture_name,
            "professor": row.professor,
            "semester": row.semester,
            "author": row.author,
            "created_at": row.created_at,
            "preview": preview,
        })

    lectures = []
    if q:
        lectures = Lecture.query.filter(
            (Lecture.name.like(like)) | (Lecture.professor.like(like))
        ).order_by(Lecture.name.asc(), Lecture.professor.asc()).limit(50).all()

    return render_template("lecture_home.html", q=q, my_point=my_point,
                           reviews=reviews, lectures=lectures)


@lecture_bp.route("/<int:lecture_id>")
def lecture_page_redirect(lecture_id):
    return redirect(url_for("lecture.lecture_reviews", lecture_id=lecture_id), 302)


@lecture_bp.route("/<int:lecture_id>/reviews", methods=["GET"], endpoint="lecture_reviews")
def lecture_reviews(lecture_id):
    lec = Lecture.query.get(lecture_id)
    if not lec:
        return "강의를 찾을 수 없습니다.", 404

    rows = LectureReview.query.filter_by(lecture_id=lecture_id).order_by(LectureReview.r_id.desc()).all()
    reviews = []
    for r in rows:
        txt = unquote(r.content) if "%" in r.content else r.content
        reviews.append({
            "r_id": r.r_id,
            "semester": r.semester,
            "content": r.content,
            "author": r.author,
            "created_at": r.created_at,
            "preview": txt[:140] + ("..." if len(txt) > 140 else "")
        })

    return render_template("lecture_page.html", lec=lec, reviews=reviews)


@lecture_bp.route("/<int:lecture_id>/reviews/write", methods=["GET"], endpoint="lecture_review_write")
def lecture_review_write(lecture_id):
    lec = Lecture.query.get(lecture_id)
    if not lec:
        return "강의를 찾을 수 없습니다.", 404
    return render_template("lecture_review.html", lec=lec)


@lecture_bp.route("/<int:lecture_id>/reviews", methods=["POST"], endpoint="lecture_review_create")
def lecture_review_create(lecture_id):
    semester = (request.form.get("semester") or "").strip()
    author = (request.form.get("author") or "익명").strip()
    content = request.form.get("content") or ""

    if not semester or not content:
        flash("학기와 내용을 입력하세요.")
        return redirect(url_for("lecture.lecture_review_write", lecture_id=lecture_id))

    lec = Lecture.query.get(lecture_id)
    if not lec:
        flash("존재하지 않는 강의입니다.")
        return redirect(url_for("lecture.lecture_home"))

    try:
        review = LectureReview(lecture_id=lecture_id, semester=semester, content=content, author=author)
        db.session.add(review)
        db.session.flush()  # review.r_id 확보

        uid = get_current_user_id()
        if uid:
            award_once(uid, +10, "LECTURE_REVIEW_CREATE", "lecture_review", review.r_id)

        db.session.commit()
        flash("등록 완료! (+10P)" if uid else "등록 완료!")
    except Exception as e:
        db.session.rollback()
        flash(f"저장 실패: {e}")
        return redirect(url_for("lecture.lecture_review_write", lecture_id=lecture_id))

    return redirect(url_for("lecture.lecture_reviews", lecture_id=lecture_id))


@lecture_bp.route("/<int:lecture_id>/exam", methods=["GET"], endpoint="lecture_exam")
def lecture_exam(lecture_id):
    lec = Lecture.query.get(lecture_id)
    if not lec:
        return "강의를 찾을 수 없습니다.", 404

    uid = get_current_user_id()
    my_point = get_user_points(uid) if uid else 0

    rows = ExamInfo.query.filter_by(lecture_id=lecture_id).order_by(ExamInfo.exam_id.desc()).all()
    exams = []
    for r in rows:
        unlocked = bool(uid and has_unlocked_exam(uid, r.exam_id))
        sect = parse_exam_body(r.body)
        exams.append({
            "exam_id": r.exam_id,
            "title": r.title,
            "body": r.body,
            "created_at": r.created_at,
            "unlocked": unlocked,
            **sect
        })

    return render_template("lecture_exam.html", lec=lec, exams=exams, my_point=my_point)


@lecture_bp.route("/<int:lecture_id>/exams", methods=["POST"], endpoint="exam_info_create")
def exam_info_create(lecture_id):
    semester = (request.form.get("semester") or "").strip()
    round_ = (request.form.get("round") or "").strip()
    strategy = (request.form.get("strategy") or "").strip()
    types = request.form.getlist("types")
    samples = [s.strip() for s in request.form.getlist("samples") if s and s.strip()]

    if not semester or not round_ or not strategy:
        flash("수강 학기, 시험 회차, 시험 전략을 입력하세요.")
        return redirect(url_for("lecture.exam_info_write", lecture_id=lecture_id))

    lec = Lecture.query.get(lecture_id)
    if not lec:
        flash("존재하지 않는 강의입니다.")
        return redirect(url_for("lecture.lecture_home"))

    title = f"{semester} {round_}"
    body_lines = ["[시험 전략]\n" + strategy]
    if types:
        body_lines.append("[문제 유형]\n" + ", ".join(types))
    if samples:
        body_lines.append("[문제 예시]\n" + "\n".join(f"{i+1}. {s}" for i, s in enumerate(samples)))
    body = "\n\n".join(body_lines)

    try:
        exam = ExamInfo(lecture_id=lecture_id, title=title, body=body)
        db.session.add(exam)
        db.session.flush()

        uid = get_current_user_id()
        if uid:
            award_once(uid, +20, "EXAM_INFO_CREATE", "exam_info", exam.exam_id)

        db.session.commit()
        flash("시험 정보가 등록되었습니다. (+20P)" if uid else "시험 정보가 등록되었습니다.")
    except Exception as e:
        db.session.rollback()
        flash(f"저장 실패: {e}")
        return redirect(url_for("lecture.exam_info_write", lecture_id=lecture_id))

    return redirect(url_for("lecture.lecture_exam", lecture_id=lecture_id))


@lecture_bp.route("/<int:lecture_id>/exams/write", methods=["GET"], endpoint="exam_info_write")
def exam_info_write(lecture_id):
    lec = Lecture.query.get(lecture_id)
    if not lec:
        return "강의를 찾을 수 없습니다.", 404
    return render_template("lecture_exam_write.html", lec=lec)


@lecture_bp.route("/exams/<int:exam_id>/view", methods=["POST"], endpoint="exam_info_view")
def exam_info_view(exam_id):
    uid = get_current_user_id()
    if not uid:
        flash("로그인이 필요합니다.")
        return redirect(url_for("auth.login"))

    exam = ExamInfo.query.get(exam_id)
    if not exam:
        return "시험정보가 없습니다.", 404

    if has_unlocked_exam(uid, exam_id):
        flash("이미 열람한 정보입니다.")
        return redirect(url_for("lecture.lecture_exam", lecture_id=exam.lecture_id))

    raw = request.form.get("point") or request.args.get("point") or "0"
    try:
        client_reported_point = int(raw)
    except ValueError:
        client_reported_point = 0

    if client_reported_point < DEFAULT_EXAM_VIEW_PRICE:
        flash("포인트가 부족합니다.\n먼저 강의평이나 시험 정보를 공유해주세요 :D")
        return redirect(url_for("lecture.lecture_exam", lecture_id=exam.lecture_id))

    add_point_event(uid, -DEFAULT_EXAM_VIEW_PRICE, "EXAM_INFO_VIEW", "exam_info", exam_id)
    db.session.commit()
    flash(f"열람되었습니다. ({DEFAULT_EXAM_VIEW_PRICE}P 차감)")

    return redirect(url_for("lecture.lecture_exam", lecture_id=exam.lecture_id))


# exam body 파싱
def parse_exam_body(body: str):
    out = {"strategy": "", "types": "", "samples": []}
    if not body:
        return out

    blocks = [b.strip() for b in body.split("\n\n") if b.strip()]
    for b in blocks:
        if b.startswith("[시험 전략]"):
            out["strategy"] = b.split("]", 1)[1].strip()
        elif b.startswith("[문제 유형]"):
            out["types"] = b.split("]", 1)[1].strip()
        elif b.startswith("[문제 예시]"):
            content = b.split("]", 1)[1].strip()
            lines = [ln.strip(" .") for ln in content.splitlines() if ln.strip()]
            out["samples"] = lines
    return out

#포인트 내역 라우터
@lecture_bp.route("/points/history", methods=["GET"], endpoint="point_history")
def point_history():
    uid = get_current_user_id()
    if not uid:
        flash("로그인이 필요합니다.")
        return redirect(url_for("auth.login"))

    # 내역 전체
    rows = PointHistory.query.filter_by(user_id=uid).order_by(PointHistory.created_at.desc()).all()

    # 총합 계산
    total_points = sum(r.delta for r in rows)

    # reason 매핑 테이블
    REASON_MAP = {
        "EXAM_INFO_CREATE": "시험 정보 공유",
        "EXAM_INFO_VIEW": "시험 정보 조회",
        "LECTURE_REVIEW_CREATE": "강의평 작성",
        "EXAM_INFO_FEEDBACK": "시험 정보 만족도 평가",
    }

    histories = []
    for r in rows:
        histories.append({
            "delta": r.delta,
            "reason": REASON_MAP.get(r.reason, r.reason),  # 매핑 없으면 원래 값 그대로
            "created_at": r.created_at.strftime("%m/%d %H:%M"),
        })

    return render_template("point_history.html", histories=histories, my_point=total_points)

