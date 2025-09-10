document.addEventListener("DOMContentLoaded", () => {
    const list = document.getElementById("comment");
    const textInput = document.getElementById("commentInput");
    const submitBtn = document.getElementById("submit-btn");
    const postId = document.getElementById("comment").dataset.postId;
    console.log(postId)

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

                    // delete-btn
                    const deleteBtn = document.createElement("button")
                    deleteBtn.classList.add("delete-btn");
                    deleteBtn.textContent = "delete"

                    // edit-btn

                    // reply-btn
                    const replyBtn = document.createElement("button")
                    replyBtn.classList.add("reply-btn");
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

    // 새 댓글 추가하기
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

    // TODO :
    async function deleteComment(id) {
      if (!confirm("정말 삭제하시겠습니까?")) return;

      const res = await fetch(`/api/v1/comments/${id}`, { method: "DELETE" });
      if (res.ok) {
        document.querySelector(`[data-comment-id='${id}']`).remove();
      } else {
        alert("댓글 삭제 실패!");
      }
    }

    submitBtn.addEventListener("click", () => {
        const text = textInput.value.trim();

        if (!text) {
            alert("작성자와 댓글 내용을 모두 입력해주세요.");
            return;
        }

        addComment(text);
    });


    loadComments();
});
