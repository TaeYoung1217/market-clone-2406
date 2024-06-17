const calcTime = (timestamp) => {
  const curTime = new Date().getTime() - 9 * 60 * 60 * 1000; //UTC+9 보정
  const time = new Date(curTime - timestamp);
  const hour = time.getHours();
  const min = time.getMinutes();
  const sec = time.getSeconds();

  if (hour > 0) return `${hour}시간 전`;
  else if (min > 0) return `${min}분 전`;
  else if (sec > 0) return `${sec}초 전`;
  else return `방금 전`;
};

const renderData = (data) => {
  const main = document.querySelector("main");
  data
    .sort((a, b) => b.id - a.id)
    .forEach(async (obj) => {
      const div = document.createElement("div");
      div.className = "item-list";

      const imgDiv = document.createElement("div");
      imgDiv.className = "item-list__img";

      const img = document.createElement("img");
      const res = await fetch(`/images/${obj.id}`); //서버에 obj.id를 기준으로 fetch(GET) 요청
      const blob = await res.blob(); //return 값을 blob 타입으로 저장 후
      const url = URL.createObjectURL(blob); //blob 타입에 대한 url 생성
      img.src = url; //img url 지정

      const InfoDiv = document.createElement("div");
      InfoDiv.className = "item-list__info";

      const InfoTitleDiv = document.createElement("div");
      InfoTitleDiv.className = "item-list__info-title";
      InfoTitleDiv.innerText = obj.title;

      const InfoMetaDiv = document.createElement("div");
      InfoMetaDiv.className = "item-list__info-meta";
      InfoMetaDiv.innerText = obj.place + " " + calcTime(obj.insertAt);

      const InfoPriceDiv = document.createElement("div");
      InfoPriceDiv.className = "item-list__info-price";
      InfoPriceDiv.innerText = obj.price;

      imgDiv.appendChild(img);

      InfoDiv.appendChild(InfoTitleDiv);
      InfoDiv.appendChild(InfoMetaDiv);
      InfoDiv.appendChild(InfoPriceDiv);
      div.appendChild(imgDiv);
      div.appendChild(InfoDiv);

      main.appendChild(div);
    });
};

const fetchList = async () => {
  const res = await fetch("/items");
  const data = await res.json();
  renderData(data);
};

fetchList();
