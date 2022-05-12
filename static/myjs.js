function go_posting() {
    window.location.href = '/go_posting'
}

// post 작성
function posting(x,y) {
    let title = $('#input-title').val()
    let file = new FormData($('#upload-file')[0])
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
    form_data.append("x_give",x)
    form_data.append("y_give",y)

    let form_data_box = new FormData()
    // form_data_box.append("contentdata", form_data)
    // form_data_box.append("filedata", form_data2)
    var form_data2 = new FormData($('#upload-file')[0]);
    $.ajax({
        type: 'POST',
        url: '/fileupload',
        data: form_data2,
        processData: false,
        contentType: false,
        success: function (data) {
            alert("파일이 업로드 되었습니다!!");
            $.ajax({
                type: "POST",
                url: "/posting",
                data: form_data_box,
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
        },
    });
}

function toggle_guide_product() {
    $("#button-guide").toggleClass("is-hidden")
}

function toggle_guide_detail() {
    $("#button-guide").toggleClass("is-hidden")
    $("#button-user").toggleClass("is-hidden")
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
                    let html_temp = `<div class="card" onclick="detail('${product['pid']}')" style="width: 350px; height: 500px; margin-bottom: 40px;">
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

function detail(pid) {
    window.location.href = `/product/${pid}`
}

function edit_product(pid) {
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
    form_data.append("pid", pid)

    $.ajax({
        type: "POST",
        url: "/edit_posting",
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

function delete_product(pid) {
    $.ajax({
        type: "POST",
        url: "/delete_product",
        data: {"pid_give":pid},
        success: function (response) {
            alert(response["msg"])
            window.location.href = "/product"
        }
    });
}

function add_comment(pid) {
    let comment_content = $('#comment-content').val();
    let form_data = new FormData()
    form_data.append("content_give", comment_content)
    form_data.append("cid_give", pid)
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

function get_comment(cid) {
    $("#comment").empty()
    $.ajax({
        type: "GET",
        url: `/product/get_comments?cid_give=${cid}`,
        data: {},
        success: function (response) {
            let comments = response["comments"];
            console.log(comments.length)
            for (let i = 0; i < comments.length; i++) {
                let comment = comments[i];
                let html_temp = `<div id="box-outline" class="box">
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

function go_bucket(pid) {
    $.ajax({
        type: "POST",
        url: `/product/bucket`,
        data: {"pid_give":pid},
        success: function (response) {
            if (response["result"] == "success") {
                alert(response["msg"])
            }
        }
    });
}

function toggle_bucket(pid, type) {
    console.log(pid, type)
    let $a_bucket = $(`#${pid} a[aria-label='${type}']`)
    let $i_bucket = $a_bucket.find("i")
    let on_bucket = {"star":"fa-star"}
    let off_bucket = {"star":"fa-star-o"}
    if ($i_bucket.hasClass(on_bucket[type])) {
        $.ajax({
            type: "POST",
            url: "/update_bucket",
            data: {
                pid_give: pid,
                type_give: type,
                action_give: "off_bucket"
            },
            success: function (response) {
                console.log("unlike")
                $i_bucket.addClass(off_bucket[type]).removeClass(on_bucket[type])
            }
        })
    } else {
        $.ajax({
            type: "POST",
            url: "/update_bucket",
            data: {
                pid_give: pid,
                type_give: type,
                action_give: "on_bucket"
            },
            success: function (response) {
                console.log("on_bucket")
                $i_bucket.addClass(on_bucket[type]).removeClass(off_bucket[type])
            }
        })
    }
}


// function delete_comment(commentid) {
//     $.ajax({
//         type: "POST",
//         url: "/delete_comment",
//         data: {"commentid_give":commentid},
//         success: function (response) {
//             alert(response["msg"])
//             window.location.reload()
//         }
//     });
// }