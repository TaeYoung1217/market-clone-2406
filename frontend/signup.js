const form = document.getElementById("signup-form");

const checkPassword = () => {
  const formData = new FormData(form);
  const password1 = formData.get("password");
  const password2 = formData.get("password2");

  if (password1 === password2) {
    return true;
  } else return false;
};

const handleSubmit = async (event) => {
  event.preventDefault();
  const div = document.getElementById("info");
  const formData = new FormData(form); //입력 form에서 받아온 내용을 FormData객체로 받아옴
  const sha256Password = sha256(formData.get("password")); //받아온 password 해시암호화
  formData.set("password", sha256Password); //formData에 있는 패스워드를 암호화된 패스워드로 다시 값 설정

  if (checkPassword()) {
    const res = await fetch("/signup", {
      method: "POST",
      body: formData,
    });

    const data = await res.json();
    if (data === "200") {
      alert("회원가입에 성공했습니다");
      window.location.pathname = "/login.html";
    } else if (data === "duplicated id") {
      div.innerText = "";
      const id = document.getElementById("idform");

      const idError = document.createElement("div");

      idError.innerText = "중복된 아이디 입니다.";
      idError.style.color = "red";
      id.appendChild(idError);
    }
  } else {
    div.innerText = "비밀번호가 다릅니다.";
    div.style.color = "red";
  }
};
form.addEventListener("submit", handleSubmit);
