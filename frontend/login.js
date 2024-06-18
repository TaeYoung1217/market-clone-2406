const form = document.getElementById("login-form");
const div = document.createElement("div");

const handleSubmit = async (event) => {
  event.preventDefault();

  const formData = new FormData(form); //입력 form에서 받아온 내용을 FormData객체로 받아옴
  const sha256Password = sha256(formData.get("password")); //받아온 password 해시암호화

  formData.set("password", sha256Password); //formData에 있는 패스워드를 암호화된 패스워드로 다시 값 설정

  const res = await fetch("/login", {
    //login으로 fetch 요청
    method: "POST",
    body: formData,
  });

  const data = await res.json();
  const accessToken = data;
  window.localStorage.setItem("token", accessToken); //로컬스토리지에 저장
  //window.sessionStorage.setItem("token", accessToken); //세션스토리지에 저장

  alert("로그인 되었습니다");

  window.location.pathname = "/";

  //   const btn = document.createElement("button");
  //   btn.innerText = "상품가져오기";
  //   btn.addEventListener("click", async () => {
  //     const res = await fetch("/items", {
  //       headers: { Authorization: `Bearer ${accessToken}` }, //accesstoken 사용시 Bearer 사용
  //     });
  //     const data = await res.json();
  //     console.log(data);
  //   });

  //   infoDiv.appendChild(btn);

  //   if (res.status === 200) {
  //     // alert("로그인에 성공");
  //     // window.location.pathname = "/";
  //   } else if (res.status === 401) {
  //     div.innerText = "ID 또는 비밀번호가 일치하지 않습니다";
  //     div.style.color = "red";

  //     form.appendChild(div);
  //   }
};
form.addEventListener("submit", handleSubmit);
