// like 부분 숫자 계산
function toggle_like(post_id, type) {
    console.log(post_id, type)
    let $a_like = $(`#${post_id} a[aria-label='${type}']`)
    let $i_like = $a_like.find("i")
    let like = {"heart":"fa-heart", "thumbs":"fa-thumbs-up", "thumbs_down":"fa-thumbs-down"}
    let no_like = {"heart":"fa-heart-o", "thumbs":"fa-thumbs-o-up", "thumbs_down":"fa-thumbs-o-down"}
    if ($i_like.hasClass(like[type])) {
        $.ajax({
            type: "POST",
            url: "/update_like",
            data: {
                post_id_give: post_id,
                type_give: type,
                action_give: "unlike"
            },
            success: function (response) {
                console.log("unlike")
                $i_like.addClass(no_like[type]).removeClass(like[type])
                $a_like.find("span.like-num").text(num2str(response["count"]))
            }
        })
    } else {
        $.ajax({
            type: "POST",
            url: "/update_like",
            data: {
                post_id_give: post_id,
                type_give: type,
                action_give: "like"
            },
            success: function (response) {
                console.log("like")
                $i_like.addClass(like[type]).removeClass(no_like[type])
                $a_like.find("span.like-num").text(response["count"])
            }
        })
    }
}

// post 작성
function post() {
    let name = $('#input-name-pic').val()
    let file = $('#input-picture')[0].files[0]
    let comment = $("#textarea-comment").val()
    let today = new Date().toISOString()
    // form_data 초기화
    let form_data = new FormData()
    form_data.append("file_give", file)
    form_data.append("name_give", name)
    form_data.append("comment_give", comment)
    form_data.append("date_give", today)
    console.log(name, file, comment, today, form_data)

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
                window.location.reload()
            }
        }
    });
}

function detail(title) {
    window.location.href = `/product/${title}`
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
        url: `/get_products?username_give=${username}`,
        data: {},
        success: function (response) {
            if (response["result"] == "success") {
                let products = response["products"]
                for (let i = 0; i < products.length; i++) {
                    let product = products[i]
                    let time_product = new Date(post["date"])
                    let time_before = time2str(time_product)
                    let mean = post['mean']
                    let html_temp = `<div class="card" id="${product["_id"]}" onclick="detail(${product['title']}})" style="max-width: 300px; margin-top: 2rem">
                                         <div class="card-image">
                                             <figure class="image is-4by3">
                                                 <img src="../static/post_pics/${product.file}" class="card-img-top" alt="Placeholder image">
                                             </figure>
                                         </div>
                                         <div class="card-content">
                                             <div class="media">
                                                 <div class="media-content">
                                                     <p class="title is-4">${product['title']}</p>
                                                     <p class="subtitle is-6">${product['date']}</p>
                                                     <small style="float:right;">${time_before}</small>
                                                 </div>
                                             </div>
                                             <nav class="level is-mobile">
                                                 <div class="level-left">
                                                     <a class="level-item is-sparta" aria-label="grade">
                                                         <span class="icon is-small"><i class="fa-solid fa-star"></i></span>&nbsp;<span class="like-num">${mean}</span>
                                                     </a>
                                                 </div>
                                             </nav>
                                         </div>
                                     </div>`
                    $("#post-box").append(html_temp)
                }
            }
        }
    })
}

function get_comment() {
    $("#media-comment").empty()
    $.ajax({
        type: "GET",
        url: `/product?title_give=${title}`,
        data: {},
        success: function (response) {
            let comments = response["comments"];
            for (let i = 0; i < comments.length; i++) {
                let comment = comments[i]["comment"];
                let html_temp = `<figure class="media-left">
                                         <p class="image is-64x64">
                                             <img src="{{ product.user_pic }}">
                                         </p>
                                     </figure>
                                     <div class="media-content">
                                         <div class="field">
                                             <p class="control">${comment}</p>
                                         </div>
                                     </div>`
                $("#media-comment").append(html_temp)
            }
        }
    });
}

function toggle_guide() {
    $("#media_guide").toggleClass("is-hidden")
    $("#button_guide").toggleClass("is-hidden")
    $("#button_user").toggleClass("is-hidden")
}

function add_comment() {
    let new_comment = $('#new-comment').val();
    $.ajax({
        type: "POST",
        url: `/api/add_comment`,
        data: {
            comment_give: new_comment
        },
        success: function (response) {
            get_comment();
            $('#new-comment').val("");
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
    $.ajax({
        type: "POST",
        url: `/api/delete_word`,
        data: {},
        success: function (response) {
            alert(response["msg"])
            window.location.href = "/"
        }
    });
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
