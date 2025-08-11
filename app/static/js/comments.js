document.addEventListener("DOMContentLoaded", () => {
    const list = document.getElementById("parent");
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
                    const li = document.createElement("li");
                    li.textContent = `${comment.author_id}: ${comment.text}`;
                    list.appendChild(li);
                });
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
                li.textContent = `${comment.author_id}: ${comment.text}`;
                list.appendChild(li);

                // 입력창 초기화
                textInput.value = "";
            })
            .catch(err => {
                alert("댓글 작성 실패: " + (err.error || "알 수 없는 오류"));
            });
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
