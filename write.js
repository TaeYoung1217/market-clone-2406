const handleSubmitForm = async (event) => {
  event.preventDefault(); //redirect 방지
  const body = new FormData(form);
  body.append("insertAt", new Date().getTime());
  const accessToken = window.localStorage.getItem("token");
  try {
    //에러처리
    const res = await fetch("/items", {
      headers: { Authorization: `Bearer ${accessToken}` },
      method: "POST",
      body,
    });

    const data = await res.json();
    if (data === "200") {
      window.location.pathname = "/";
    }
  } catch (e) {
    console.error("업로드에 실패했습니다");
  }
};

const form = document.getElementById("write-form");
form.addEventListener("submit", handleSubmitForm);
