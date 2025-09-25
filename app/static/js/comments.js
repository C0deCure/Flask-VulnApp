document.addEventListener("DOMContentLoaded", () => {
    const list = document.getElementById("comment");
    const textInput = document.getElementById("commentInput");
    const submitBtn = document.getElementById("submit-btn");
    const postId = document.getElementById("comment").dataset.postId;
    const currentUserId = document.getElementById("comment").dataset.currentUserId;

    // 댓글 목록 불러오기
    function loadComments() {
        fetch("/api/v1/comments/"+postId)
            .then(res => res.json())
            .then(data => {
                data.forEach(comment => {
                    // parent Div
                    const parentDiv = document.createElement("div");
                    parentDiv.classList.add("parent");
                    parentDiv.setAttribute('data-comment-id', comment.id);

                    // reply-btn
                    const replyBtn = document.createElement("button")
                    replyBtn.className = "reply-btn btn btn-sm btn-outline-primary";
                    replyBtn.textContent = "reply"

                    // profile image
                    const img = document.createElement("img");
                    img.classList.add("commentpro");
                    // if you want to make image different for eacg user.id, ...
                    img.src = "/static/images/0.png";

                    // username
                    const h3 = document.createElement("h3");
                    h3.classList.add("medium");
                    h3.textContent = comment.user_name || "(unknown)";

                    // comment content
                    const p = document.createElement("p");
                    p.classList.add("large");
                    p.textContent = comment.text;

                    // edit-btn and delete-button
                    if (currentUserId && comment.user_id == currentUserId) {
                        // 삭제 버튼 (a 태그 대신 button 사용을 권장)
                        const deleteBtn = document.createElement("button");
                        deleteBtn.onclick = () => handleDelete(comment.id);
                        // Bootstrap 버튼 스타일 적용
                        deleteBtn.className = "delete btn btn-sm btn-outline-primary ms-2";
                        deleteBtn.textContent = "삭제";

                        // 수정 버튼
                        const editBtn = document.createElement("button");
                        // Bootstrap 버튼 스타일 적용
                        editBtn.className = "edit btn btn-sm btn-outline-primary ms-2"; // margin-left 추가
                        editBtn.textContent = "수정";

                        editBtn.onclick = () => {
                            // 1. 폼에 현재 댓글 ID와 텍스트 채우기
                            hiddenCommentIdInput.value = comment.id;
                            newContentInput.value = comment.text;
                            modalResultMessage.textContent = ''; // 이전 오류 메시지 초기화

                            // 2. Bootstrap 모달 인스턴스를 통해 모달 보이기
                            editModal.show();
                        };

                        // 생성된 버튼들을 댓글 div에 추가
                        parentDiv.appendChild(deleteBtn);
                        parentDiv.appendChild(editBtn);
                    }

                    // append elements
                    parentDiv.appendChild(img);
                    parentDiv.appendChild(h3);
                    parentDiv.appendChild(p);
                    parentDiv.appendChild(replyBtn);

                    list.appendChild(parentDiv);
                });

                addReplyFormToComment();
            });
    }

    // 새 댓글
    // TODO :
    function addComment(text) {
        fetch("/api/v1/comments", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ text }),
        })
            .then(res => {
                if (!res.ok) {
                    return res.json().then(err => Promise.reject(err));
                }
                return res.json();
            })
            .then(comment => {
                // 성공하면 화면에 바로 추가
                const li = document.createElement("li");
                li.textContent = `${comment.user_name}: ${comment.text}`;
                list.appendChild(li);

                // 입력창 초기화
                textInput.value = "";
            })
            .catch(err => {
                alert("댓글 작성 실패: " + (err.error || "알 수 없는 오류"));
            });
    }

    function addReplyFormToComment(){
        document.querySelectorAll(".reply-btn").forEach(btn => {
            btn.addEventListener("click", function() {
                const commentDiv = btn.closest(".parent");
                const commentId = commentDiv.getAttribute("data-comment-id");

                // 숨겨진 폼 가져오기
                const replyForm = document.getElementById("replyForm");
                const newForm = replyForm.cloneNode(true);

                // parent_id 세팅
                newForm.querySelector('[name="parent_id"]').value = commentId;

                // 해당 댓글 바로 아래로 폼 이동시키기
                commentDiv.appendChild(newForm);

            });
        });
    }

    // 삭제 처리를 위한 비동기 함수
    async function handleDelete(commentId) {
        // 사용자에게 정말 삭제할 것인지 한 번 더 확인
        if (!confirm("정말로 이 댓글을 삭제하시겠습니까?")) {
            return; // 사용자가 '취소'를 누르면 함수 종료
        }

        try {
            const response = await fetch(`/api/v1/comments/${commentId}`, {
                method: 'DELETE' // HTTP 요청 방식을 'DELETE'로 지정
            });

            if (response.ok) { // 요청이 성공했다면 (상태 코드 200-299)
                alert("댓글이 성공적으로 삭제되었습니다.");

                // 화면에서 해당 댓글 요소(div)를 찾아 제거
                const commentElement = document.querySelector(`.parent[data-comment-id='${commentId}']`);
                if (commentElement) {
                    commentElement.remove();
                }
            } else { // 요청이 실패했다면
                const errorData = await response.json();
                alert(`오류: ${errorData.description || '삭제에 실패했습니다.'}`);
            }
        } catch (error) {
            console.error('Delete Error:', error);
            alert("네트워크 오류가 발생했습니다. 다시 시도해주세요.");
        }
    }

    function updateVoteButtons(widget, userVote) {
        const upvoteBtn = widget.querySelector('.upvote');
        const downvoteBtn = widget.querySelector('.downvote');

        // 모든 활성 클래스 초기화
        upvoteBtn.classList.remove('active');
        downvoteBtn.classList.remove('active');

        if (userVote === 1) {
            upvoteBtn.classList.add('active'); // 예: .active { color: orange; }
        } else if (userVote === -1) {
            downvoteBtn.classList.add('active'); // 예: .active { color: dodgerblue; }
        }
    }

    submitBtn.addEventListener("click", () => {
        const text = textInput.value.trim();

        if (!text) {
            alert("작성자와 댓글 내용을 모두 입력해주세요.");
            return;
        }

        // addComment(text);
    });

    document.querySelectorAll('.vote-widget').forEach(widget => {
        widget.addEventListener('click', async (event) => {
            // vote-btn 클래스를 가진 버튼이 클릭되었을 때만 실행
            if (!event.target.classList.contains('vote-btn')) {
                return;
            }

            const postId = widget.dataset.postId;
            const value = parseInt(event.target.dataset.value, 10);

            try {
                const response = await fetch(`/api/v1/posts/${postId}/vote`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        // CSRF 토큰 헤더가 필요하다면 여기에 추가
                    },
                    body: JSON.stringify({ value: value })
                });

                if (!response.ok) {
                    // 로그인하지 않았거나 다른 에러 발생 시
                    const errorData = await response.json();
                    alert(errorData.description || '투표에 실패했습니다.');
                    return;
                }

                const data = await response.json();

                // API 응답 값으로 화면의 총 투표 수와 버튼 상태를 업데이트
                const totalVotesSpan = widget.querySelector('.total-votes');
                totalVotesSpan.textContent = data.total_votes;

                // (심화) 사용자의 투표 상태에 따라 버튼 색상을 변경하는 로직 추가
                updateVoteButtons(widget, data.user_vote);

            } catch (error) {
                console.error('Error:', error);
                alert('네트워크 오류가 발생했습니다.');
            }
        });
    });

    // ===== 모달의 '수정 완료' 버튼 로직 수정 =====
    editForm.addEventListener('submit', async (event) => {
        event.preventDefault();

        const commentId = hiddenCommentIdInput.value;
        const newContent = newContentInput.value;
        console.log(newContent)

        try {
            const response = await fetch(`/api/v1/comments/${commentId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: newContent })
            });

            const data = await response.json();

            if (response.ok) {
                // 성공 시 Bootstrap 모달 닫기
                editModal.hide();

                // 화면의 댓글 내용 바로 업데이트
                const commentTextElement = document.querySelector(`.parent[data-comment-id='${commentId}'] p.large`);
                if (commentTextElement) {
                    commentTextElement.textContent = data.comment.content;
                }
            } else {
                // 실패 시 모달 안에 오류 메시지 표시
                modalResultMessage.textContent = `오류: ${data.description || '수정에 실패했습니다.'}`;
            }
        } catch (error) {
            console.error('Update Error:', error);
            modalResultMessage.textContent = "네트워크 오류가 발생했습니다.";
        }
    });

    loadComments();
});

