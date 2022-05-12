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

    // let form_data_box = new FormData()
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

function toggle_user_bucket() {
    $("#bucket-on").toggleClass("is-hidden")
    $("#bucket-off").toggleClass("is-hidden")
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
function get_products_index(username) {
    if (username == undefined) {
        username=""
    }
    $("#product-box").empty()
    $.ajax({
        type: "GET",
        url: `/product/get_index`,
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
                                                 <img src="../static/${product['file']}" class="card-img-top" alt="Placeholder image">
                                             </figure>
                                         </div>
                                         <div class="card-content">
                                             <div class="media">
                                                 <div class="media-content">
                                                     <p id="search-box" class="title is-4">${product['title']}</p>
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
                                                 <img src="../static/${product['file']}" class="card-img-top" alt="Placeholder image">
                                             </figure>
                                         </div>
                                         <div class="card-content">
                                             <div class="media">
                                                 <div class="media-content">
                                                     <p id="search-box" class="title is-4">${product['title']}</p>
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

function go_editing(pid) {
    window.location.href = `/go_editing?pid_give=${pid}`
}

// function edit_product(x, y, pid) {
//     let title = $('#input-title').val()
//     let file = new FormData($('#upload-file')[0])
//     let content = $("#input-content").val()
//     let calender = $("#input-calender").val()
//     let price = $("#input-price").val()
//     let today = new Date().toISOString()
//     // form_data 초기화
//     let form_data = new FormData()
//     form_data.append("title_give", title)
//     form_data.append("file_give", file)
//     form_data.append("pid_give", pid)
//     form_data.append("content_give", content)
//     form_data.append("calender_give", calender)
//     form_data.append("price_give", price)
//     form_data.append("date_give", today)
//     form_data.append("x_give",x)
//     form_data.append("y_give",y)
//
//     // let form_data_box = new FormData()
//     // form_data_box.append("contentdata", form_data)
//     // form_data_box.append("filedata", form_data2)
//     var form_data2 = new FormData($('#upload-file')[0]);
//     $.ajax({
//         type: 'POST',
//         url: '/fileupload',
//         data: form_data2,
//         processData: false,
//         contentType: false,
//         success: function (data) {
//             alert("파일이 업로드 되었습니다!!");
//             $.ajax({
//                 type: "POST",
//                 url: "/posting",
//                 data: form_data,
//                 cache: false,
//                 contentType: false,
//                 processData: false,
//                 success: function (response) {
//                     if (response["result"] == "success") {
//                         alert(response["msg"])
//                         window.location.href = `/product/${pid}`
//                     }
//                 }
//             });
//         },
//     });
// }

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
                // alert(response["msg"])
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
            for (let i = comments.length - 1; i >= 0; i--) {
                let comment = comments[i];
                let x = comment["cid"];
                let y = comment["pcid"];
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
                                     <nav id="btns-me" class="level is-mobile" style="margin-top:2rem">
                                         <a class="button level-item has-text-centered is-sparta" aria-label="edit" onclick='$("#modal-edit").addClass("is-active")'>
                                             댓글 수정&nbsp;&nbsp;&nbsp;<span class="icon is-small"><i class="fa fa-pencil" aria-hidden="true"></i></span>
                                         </a>
                                         <div class="level-item">
                                             <a class="button is-sparta" onclick="delete_comment(${x},${y})">삭제</a>
                                         </div>
                                     </nav>
                                     <div class="modal" id="modal-edit">
                                        <div class="modal-background" onclick='$("#modal-edit").removeClass("is-active")'></div>
                                        <div class="modal-content">
                                            <div class="box">
                                                <article class="media">
                                                    <div class="media-content">
                                                        <div class="field">
                                                            <label class="label" for="textarea-comment">댓글</label>
                                                            <p class="control">
                                                                <textarea id="textarea-comment" class="textarea" placeholder="내용">
                                                                    ${comment['content']}
                                                                </textarea>
                                                            </p>
                                                        </div>
                                                        <nav class="level is-mobile">
                                                            <div class="level-left">
                                                            </div>
                                                            <div class="level-right">
                                                                <div class="level-item">
                                                                    <a class="button is-sparta"
                                                                       onclick="edit_comment(${x},${y})">업데이트</a>
                                                                </div>
                                                                <div class="level-item">
                                                                    <a class="button is-sparta is-outlined"
                                                                       onclick='$("#modal-edit").removeClass("is-active")'>취소</a>
                                                                </div>
                                                            </div>
                                                        </nav>
                                                    </div>
                                                </article>
                                            </div>
                                        </div>
                                        <button class="modal-close is-large" aria-label="close"
                                                onclick='$("#modal-edit").removeClass("is-active")'></button>
                                    </div>
                                 </div>`
                $("#comment").append(html_temp)
            }
        }
    });
}

// function edit_comment(cid, pcid) {
//     let comment_edit = $('#textarea-comment').val();
//     let form_data = new FormData()
//     form_data.append("cid_give", cid)
//     form_data.append("pcid_give", pcid)
//     form_data.append("comment_give", comment_edit)
//     $.ajax({
//         type: "POST",
//         url: "/product/edit_comments",
//         data: form_data,
//         cache: false,
//         contentType: false,
//         processData: false,
//         success: function (response) {
//             alert(response["msg"])
//             window.location.reload()
//         }
//     })
// }

function delete_comment(cid, pcid) {
    $.ajax({
        type: "POST",
        url: "/delete_comment",
        data: {
            "pcid_give":pcid
        },
        success: function (response) {
            alert(response["msg"])
            window.location.href = `/product/${cid}`
        }
    });
}

function on_bucket(pid) {
    $.ajax({
        type: "POST",
        url: "/on_bucket",
        data: {
            pid_give: pid,
            action_give: 'on_bucket'
        },
        success: function (response) {
            alert(response["msg"])
            window.location.reload()
        }
    })
}

function off_bucket(pid) {
    $.ajax({
        type: "POST",
        url: "/off_bucket",
        data: {
            pid_give: pid
        },
        success: function (response) {
            alert(response["msg"])
            window.location.reload()
        }
    })
}

// 이미지 불러오기
// function getFiles() {
//     $.ajax({
//         type: 'GET',
//         url: '/download',
//         success: function (data) {
//             alert('done')
//         },
//     });
// }
//
// function makeOrder(data) {
//     let order = `<tr>
//                      <td><img width="200px" src="/${data}"></td>
//                  </tr>`;
//     $("#orders-box").append(order);
// }

function get_buckets(username) {
    if (username == undefined) {
        username=""
    }
    $("#bucket_list").empty()
    $.ajax({
        type: "GET",
        url: `/mybucket`,
        data: {},
        success: function (response) {
            if (response["result"] == "success") {
                let bucket = response["buckets"]
                let buckets = JSON.parse(bucket)
                for (let i = 0; i < buckets.length; i++) {
                    let bucket = buckets[i]
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
                    $("#bucket_list").append(html_temp)
                }
            }
        }
    })
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// // 즐겨찾기 추가 예정
// function toggle_favorites(pid, type) {
//     console.log(pid, type)
//     let $a_favorite = $(`#${pid} a[aria-label='${type}']`)
//     let $i_favorite = $a_favorite.find("i")
//     let on_favorite = {"star":"fa-star"}
//     let off_favorite = {"star":"fa-star-o"}
//     if ($i_favorite.hasClass(on_favorite[type])) {
//         $.ajax({
//             type: "POST",
//             url: "/update_favorite",
//             data: {
//                 pid_give: pid,
//                 type_give: type,
//                 action_give: "off_favorite"
//             },
//             success: function (response) {
//                 $i_favorite.addClass(off_favorite[type]).removeClass(on_favorite[type])
//                 alert(response["msg"])
//             }
//         })
//     } else {
//         $.ajax({
//             type: "POST",
//             url: "/update_favorite",
//             data: {
//                 pid_give: pid,
//                 type_give: type,
//                 action_give: "on_favorite"
//             },
//             success: function (response) {
//                 $i_favorite.addClass(on_favorite[type]).removeClass(off_favorite[type])
//                 alert(response["msg"])
//             }
//         })
//     }
// }

// // 댓글 삭제 추가 예정
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

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////