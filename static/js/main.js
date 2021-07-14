const socket = io.connect("http://" + document.domain + ":" + location.port);
let pos_count = 0, neg_count = 0, inter_count = 0, total_count = 0;
$('#popover').popover();
// const email = $('#loginemail').val();
console.log("email from home page:"+email);
socket.on("connect", () => {
  console.log("Successfully connected!");

  socket.emit("joined", {
    user: username,
    
  });

  socket.on("status", (data) => {
    // SET THE DATA INTO A HTML ELEMENT! -->COMING FROM SERVER (INIT_MSG)
    console.log("COMING FROM STATUS FN " + data.user + data.msg);
    // outputUsers(data.userList);
    
    displayMessage(data);
  });

  socket.on("userlist", (data) => {
    console.log("[User list recieved.......]", data);
    outputUsers(data);
  });

  $("#chat-form").submit(function (e) {
    e.preventDefault();
    var chatMessage = $("#myMessage").val();
    if (!chatMessage) {
      return false;
    }
    console.log(chatMessage);
    socket.emit("message", {
      user: username,
      msg: chatMessage,
    });
    $("#myMessage").val("").focus();
  });
  $("#sendbutton").click(function () {
    var chatMessage = $("#myMessage").val();
    if (!chatMessage) {
      return false;
    }
    console.log(chatMessage);
    socket.emit("message", {
      user: username,
      msg: chatMessage,
    });
    $("#myMessage").val("").focus();
  });

  $("#modal-btn1").click(function () {
    console.log("Leave Button Clicked!");
    socket.emit("leave", {
      user: username,
      email: email,
    });
  });

  socket.on("userResult", (data) => {
    console.log('[SENTIMENT RESULTS]....');
    displaySentiment(data);
  });

  socket.on("init_message", (data) => {
    console.log("COMING FROM MESSAGE FN" + data.user + data.msg);
    // console.log("Email from home page:"+email);
    displayMessage(data);
    const msg_box = document.querySelector(".message_holder");
    msg_box.scrollTop = msg_box.scrollHeight;
  });

  socket.on("message", (data) => {
    // SET THE DATA INTO A HTML ELEMENT! --> COMING FROM SERVER (ORIGINAL MSG)
    console.log("COMING FROM MESSAGE FN" + data.user + data.msg);
    console.log(data.result.final_verdict + data.result.tags + data.result.total_tags);
    processUserMessage(data);
    const msg_box = document.querySelector(".message_holder");
    msg_box.scrollTop = msg_box.scrollHeight;

  });
});

function displaySentiment(data) {
  console.log(data);
  let neg_percent = Math.round((neg_count / total_count) * 100);
  let inter_percent = Math.round((inter_count / total_count) * 100);
  let progress;
  if (neg_percent > 0) {
    progress = `<h2 class="bold1">Toxicity Meter</h2><br>
    <div class="progress">
      <div class="progress-bar progress-bar-striped progress-bar-animated bg-danger" role="progressbar" style="width: ${neg_percent}%;"><b>${neg_percent}%</b></div>
    </div>`; 
  } else if(neg_percent == 0 && inter_percent > 0) {
    inter_percent = inter_percent / 2;
    progress = `<h2 class="bold1">Toxicity Meter</h2>
    <div class="progress">
      <div class="progress-bar progress-bar-striped progress-bar-animated bg-danger" role="progressbar" style="width: ${inter_percent}%;"><b>${inter_percent}%</b></div>
    </div>`;
  } else {
    progress = `<h2 style="
    text-align: center;
">No Toxicity was detected.<br>Keep spreading Positivity!!!</h2>`; 
  }
  $("div.toxicity").append(progress);

  const score_div = document.getElementById('score');
  const h2 = document.createElement('h2');
  h2.innerHTML += "Mental State Score";
  h2.classList.add('bold1');
  score_div.appendChild(h2);
  const h3 = document.createElement('h3');
  h3.innerHTML += `Your score is: ${data.tcomp}% `
  h3.classList.add('bold1');
  score_div.appendChild(h3);
  let emoji = document.getElementById(data.verdict);
  emoji.classList.remove('dimemoji');
  const count_div = document.getElementById('count');
  const h5 = document.createElement('h5');
  h5.innerHTML += `We found <strong>${data.tp}</strong> positive comments, <strong>${data.tneg}</strong> negative comments and <strong>${data.tneu}</strong> neutral comments.`
  // h5.classList.add('bold');
  count_div.appendChild(h5);
}

function displayMessage(data) {
  let message = `<div class="message"> <p class="meta">${data.user} </p> <p class="text" style="font-weight:600"> ${data.msg}</p></div>`;
  $("div.message_holder").append(message);
}

function processUserMessage(data) {
  total_count++;
  if(data.result.score >= 50) {
    let icon_value = 'fa-exclamation icon-wrong';
    displayUserMessage(icon_value, data);
    neg_count++;
  }
  else if (data.result.score < 50 && data.result.total_tags > 0){
    let icon_value = 'fa-exclamation icon-amber';
    data.result.final_verdict = "We see something suspicious"
    displayUserMessage(icon_value, data);
    inter_count++;
  }
  else {
    let icon_value = 'fa-check icon-check';
    data.result.tags = "We couldn't find anything"
    displayUserMessage(icon_value, data);
    pos_count++;
  }
}

//<span>&nbsp&nbsp<i class="fa fa-exclamation icon-wrong" data-toggle="popover" data-trigger="hover" title = "Tags" data-content="hello" data-placement="right"aria-hidden="true"></i></span>

function displayUserMessage(icon, data) {
  const i = `<span>&nbsp;&nbsp;<i class="fa ${icon}" data-toggle="popover" data-trigger="hover" title = "${data.result.final_verdict}" data-content="Tags: ${data.result.tags}" data-placement="right" aria-hidden="true"></i></span>`;
  const div = document.createElement('div');
  div.classList.add('message');
  const p = document.createElement('p');
  p.classList.add('meta');
  p.innerText = data.user;
  p.innerHTML += i;
  div.appendChild(p);
  const para = document.createElement('p');
  para.classList.add('text');
  para.classList.add('bold');
  para.innerText = data.msg;
  div.appendChild(para);
  document.querySelector('.message_holder').appendChild(div); 
  $("#popover").hover($(() => {
    $('[data-toggle="popover"]').popover()
  }));
}

function changeRange(OldValue) {
  NewValue = (((OldValue - (-100)) * 100) / 200) + 0;
  return NewValue;
}
function outputUsers(users) {
  
  $("#users").empty();

  for(let username in users) {
    let userEmoji = 1000;
    let value;
    if(users[username] == 999) {
      userEmoji = '👋';    
    } else{
    value = changeRange(users[username]);
    if(value>80){
      userEmoji = '😄';
    }
    else if(value>60 && value<=80)
    {
      userEmoji = '😃';
    }
    else if(value>40 && value<=60)
    {
      userEmoji = '🙂';
    }
    else if(value>20 && value<=40)
    {
      userEmoji = '😩';
    }
    else {
      userEmoji = '😖';
    }
  }
    console.log(users[username],value);
    let newUser = `
    <li> 
      <div class="container">
        <div class="row">
          <div class="col-sm-6">
            ${username}
          </div>
          <div class="col-sm-6" style="text-align: right">
            ${userEmoji}
          </div>   
        </div>
      </div>  
    </li>`;
    $("#users").append(newUser);
  };
}


// $(document).on("click", "button#usersemi" , function () {
//   console.log("semicircle modAL");
  
//   $("#semicircle_container").empty();
//   var container = document.getElementById("semicircle_container");
//   var bar = new ProgressBar.SemiCircle(container, {
//     strokeWidth: 3,
//     color: "#3a3a3a",
//     trailColor: "#eee",
//     trailWidth: 3,
//     easing: "easeInOut",
//     duration: 1500,
//     from: { color: "#FF1000" },
//     to: { color: "#10FF00" },
//     // Set default step function for all animate calls
//     step: (state, bar) => {
//       bar.path.setAttribute("stroke", state.color);
//       var value = Math.round(bar.value() * 100);
//       bar.setText("Score: " + value + "%");
//       bar.text.style.color = state.color;
//     },
//   });
  // bar.text.style.fontFamily = '"Raleway", Helvetica, sans-serif';
  // bar.text.style.fontSize = "1rem";

//   bar.animate(value); // Number from 0.0 to 1.0
// });
const modal = document.querySelector("#my-modal1");
const modalBtn = document.querySelector("#modal-btn1");
// const closeBtn = document.querySelector(".close");

// Events
modalBtn.addEventListener("click", openModal);
closeBtn.addEventListener("click", closeModal);
// window.addEventListener("click", outsideClick);

// Open
function openModal() {
  modal.style.display = "block";
}

// Close
// function closeModal() {
//   modal.style.display = "none";
// }

