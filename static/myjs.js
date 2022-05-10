function go_posting() {
    window.location.href = '/go_posting'
}

// post 작성
function posting() {
    let title = $('#input-title').val()
    let file = $('#input-picture')[0].files[0]
    let content = $("#input-content").val()
    let calender = $("#input-calender").val()
    let price = $("#input-price").val()
    let today = new Date().toISOString()
    // form_data 초기화
    let form_data = new FormData()
    form_data.append("title_give", title)
    form_data.append("file_give", file)
    form_data.append("content_give", content)
    form_data.append("calender_give", calender)
    form_data.append("price_give", price)
    form_data.append("date_give", today)

    $.ajax({
        type: "POST",
        url: "/posting",
        data: form_data,
        cache: false,
        contentType: false,
        processData: false,
        success: function (response) {
            if (response["result"] == "success") {
                alert(response["msg"])
                window.location.href = `/product`
            }
        }
    });
}

function detail(product_id) {
    window.location.href = `/product/${product_id}`
}

function toggle_guide() {
    $("#media-guide").toggleClass("is-hidden")
    $("#button-guide").toggleClass("is-hidden")
    $("#button-user").toggleClass("is-hidden")
    console.log('실행!')
}

// 몇 시간 전 계산
function time2str(date) {
    let today = new Date()
    let time = (today - date) / 1000 / 60  // 분

    if (time < 60) {
        return parseInt(time) + "분 전"
    }
    time = time / 60  // 시간
    if (time < 24) {
        return parseInt(time) + "시간 전"
    }
    time = time / 24
    if (time < 7) {
        return parseInt(time) + "일 전"
    }
    return `${date.getFullYear()}년 ${date.getMonth() + 1}월 ${date.getDate()}일`
}

// like 개수 환산
function num2str(count) {
    if (count > 10000) {
        return parseInt(count / 1000) + "k"
    }
    if (count > 500) {
        return parseInt(count / 100) / 10 + "k"
    }
    if (count == 0) {
        return ""
    }
    return count
}

// 내가 쓴 post 박스 불러오기
function get_products(username) {
    if (username == undefined) {
        username=""
    }
    $("#product-box").empty()
    $.ajax({
        type: "GET",
        url: `/product/get`,
        data: {},
        success: function (response) {
            if (response["result"] == "success") {
                let product = response["products"]
                let products = JSON.parse(product)
                for (let i = 0; i < products.length; i++) {
                    let product = products[i]
                    let time_product = new Date(product["date"])
                    let time_before = time2str(time_product)
                    // let mean = product['mean']
                    let html_temp = `<div class="card" onclick="detail('${product.product_id}')" style="max-width: 300px; margin-top: 2rem">
                                         <div class="card-image">
                                             <figure class="image is-4by3">
                                                 <img src="../static/${product.file}" class="card-img-top" alt="Placeholder image">
                                             </figure>
                                         </div>
                                         <div class="card-content">
                                             <div class="media">
                                                 <div class="media-content">
                                                     <p class="title is-4">${product['title']}</p>
                                                     <p class="subtitle is-6">${product['content']}</p>
                                                     <small style="float:right;">${time_before}</small>
                                                 </div>
                                             </div>
                                             <nav class="level is-mobile">
                                                 <div class="level-left">
                                                     <a class="level-item is-sparta" aria-label="grade">
                                                         <span class="icon is-small"><i class="fa-solid fa-star"></i></span>&nbsp;<span class="like-num"></span>
                                                     </a>
                                                 </div>
                                             </nav>
                                         </div>
                                     </div>`
                    $("#product-box").append(html_temp)
                }
            }
        }
    })
}

function add_comment(product_id) {
    let comment_content = $('#comment-content').val();
    let form_data = new FormData()
    form_data.append("content_give", comment_content)
    form_data.append("product_id_give", product_id)
    $.ajax({
        type: "POST",
        url: `/product/add_comments`,
        data: form_data,
        cache: false,
        contentType: false,
        processData: false,
        success: function (response) {
            if (response["result"] == "success") {
                alert(response["msg"])
                window.location.reload()
            }
        }
    });
}

function get_comment(product_id) {
    $("#comment").empty()
    $.ajax({
        type: "GET",
        url: `/product/get_comments?product_id_give=${product_id}`,
        data: {},
        success: function (response) {
            let comments = response["comments"];
            console.log(comments.length)
            for (let i = 0; i < comments.length; i++) {
                let comment = comments[i];
                let html_temp = `<div class="box">
                                     <article class="media">
                                         <div class="media-left">
                                             <figure class="image is-64x64">
                                                 <img src="/static/${comment.user_pic_real}" alt="Image">
                                             </figure>
                                         </div>
                                         <div class="media-content">
                                             <div class="content">
                                             <p>
                                                 <strong>${comment['userid']}</strong>
                                                 <br>
                                                  ${comment['content']}
                                             </p>
                                             </div>
                                         </div>
                                     </article>
                                 </div>`
                $("#comment").append(html_temp)
            }
        }
    });
}


// function get_map() {
//     $.ajax({
//         type: "POST",
//         url: `/product/maps`,
//         data: {},
//         success: function (response) {
//             alert(response["msg"])
//             window.location.href = "/detail/{{ word }}?status=old"
//         }
//     });
// }

function go_bucket() {
    window.location.href = "/mypage/bucket"
}


function edit_product() {
    let new_ex = $('#new-example').val();
    if (!new_ex.toLowerCase().includes(word.toLowerCase())) {
        alert(`the word '${word}' is not included.`);
        return;
    }
    console.log(new_ex)
    $.ajax({
        type: "POST",
        url: `/api/save_ex`,
        data: {
            word_give: word,
            example_give: new_ex
        },
        success: function (response) {
            get_examples();
            $('#new-example').val("");
        }
    });
}

function delete_product(i) {
    console.log("deleting", i)
    $.ajax({
        type: "POST",
        url: `/api/delete_ex`,
        data: {
            word_give: word,
            number_give: i
        },
        success: function (response) {
            get_examples()
        }
    });
}