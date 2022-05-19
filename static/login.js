
window.Kakao.init('54ccebb7b25645894bc9636f54e8617a');

function kakaoLogin() {
    window.Kakao.Auth.login({
        scope: 'profile_nickname, account_email, gender', //동의항목 페이지에 있는 개인정보 보호 테이블의 활성화된 ID값을 넣습니다.
        success: function (response) {
            console.log(response) // 로그인 성공하면 받아오는 데이터
            alert(response)
            console.log(response.access_token);
            window.Kakao.API.request({ // 사용자 정보 가져오기
                url: '/v2/user/me',
                success: (res) => {
                    let kakao_account = res.kakao_account; // 계정 정보 가져옴
                    let email = kakao_account.email;
                    let nick_name = kakao_account.profile.nickname;
                    $.cookie('kakao', email, {path: '/'});
                    $.ajax({
                        type: "POST",
                        url: "/kakaologin",
                        data: {email:email, nick_name:nick_name},
                        success: function (response) {
                            // alert(response["msg"]);
                            // window.location.href='/';
                            window.location.replace("/")
                        }
                    })
                }
            });

        },
        fail: function (error) {
            console.log(error);
        }
    });
}


// function kakaoLogout() {
//     // alert('logout ok\naccess token -> ' + Kakao.Auth.getAccessToken())
//     if (!Kakao.Auth.getAccessToken()) {
//         alert('Not logged in.')
//         return
//     } else {
//         // 사용자 액세스 토큰과 리프레시 토큰을 모두 만료시킵니다. 사용자가 서비스에서 로그아웃할 때 이 API를 호출하여 더 이상 해당 사용자의 정보로 카카오 API를 호출할 수 없도록 합니다.
//         // 로그아웃 요청 성공 시, 응답 코드와 로그아웃된 사용자의 회원번호를 받습니다. 로그아웃 시에도 웹 브라우저의 카카오계정 세션은 만료되지 않고, 로그아웃을 호출한 앱의 토큰만 만료됩니다.
//         // 따라서 웹 브라우저의 카카오계정 로그인 상태는 로그아웃을 호출해도 유지됩니다. 로그아웃 후에는 서비스 초기 화면으로 리다이렉트하는 등 후속 조치를 취하도록 합니다.
//         Kakao.Auth.logout(function () {   // 로그아웃 - 쿠키에 저장된 토큰만 제거 (카카오 연동 상태는 유지)
//             // alert('logout ok\naccess token -> ' + Kakao.Auth.getAccessToken());
//             // location.href='/test'
//         })
//     }
//     window.Kakao.API.request({ // 카카오 연결 끊기
//         url: '/v1/user/unlink',
//         success: (res) => {
//             // alert('logout ok\naccess token -> ' + Kakao.Auth.getAccessToken());
//             console.log(res)
//         }
//     });
//     window.location.href = "/"
//
//
// }
