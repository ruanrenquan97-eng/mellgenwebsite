/*&中文2017-01-05姜玮111&*/
//副导航焦点定位
var leftNavFocus = {
    init: function() {
        var elnav = $("[navcrumbs]").find("a");
        var elbody = $("[navvicefocus]").find("a");
        if (elnav && elbody) {
        	for (var n = (elnav.length - 1); n >= 0; n --) {
        		$.each(elbody, function(i, item) {
	                if (elnav.eq(n).attr("href") === $(item).attr("href")) {
	                    $(item).parent().siblings().removeClass("sidenavcur");
	                    $(item).parent().addClass("sidenavcur");
	                    return false;
	                }
	            });
        	}
        }
    }
};

//主导航高亮
$(function () {
    /*如果没有各栏目的中心页面(如产品的中心页面index.aspx),
    *就指定一个默认的替代导航选中 写上要选中主导航的索引
    *一般用的最多的是资讯
    */
    var MARK = "";
    var newsDefaultURL = 7;
    var productDefaultURL = 4;
    var agentDefaultURL = 0;
    var helpDefaultURL = 9;
    var projectDefaultURL = 0;
    var downloadDefaultURL = 0;
    var jobDefaultURL = 0;
    //定义链接地址
    var current = "";
    var currentshort = "";
    //面包屑导航的获取
    var $plc = $("div.plc");
    var $plc2 = $("div.t2-wz");
    var $pro = $("div.pro_curmbs");


    /*面包屑导航的判断*/
    var $tmp = $plc.size() ? $plc : $plc2;
    var $location = $tmp.size() ? $tmp : $pro;
    //主导航的父级DIV
    var $menu = $("div.menu");
    //主导航的li,仅能选中一级,不带下拉列表样式
    var $menuli = $menu.find("ul").eq(0).children("li");
    //面包屑导航的超链接
    var $info = $location.find("a");
    //面包屑导航超链接的数量
    var count = $info.size();
    //定义选中样式
    var _cur = "cur";
    //取消所有选中
    $menu.find("li").removeClass(_cur);
    //定义一个对象
    var Obj = new Object();
    
    //给对象添加一个方法,用来获取默认的链接地址
    Obj.getCurrentURL = function () {
        //判断MARK
        //并查看是取默认MARK 还是取之前定义好的替代栏目导航
        switch (MARK) {
            case "product":
                current = productDefaultURL ? productDefaultURL : MARK;
                break;
            case "news":
                current = newsDefaultURL ? newsDefaultURL : MARK;
                break;
            case "project":
                current = projectDefaultURL ? projectDefaultURL : MARK;
                break;
            case "agent":
                current = agentDefaultURL ? agentDefaultURL : MARK;
                break;
            case "help":
                current = helpDefaultURL ? helpDefaultURL : MARK;
                break;
            case "download":
                current = downloadDefaultURL ? downloadDefaultURL : MARK;
                break;
            case "job":
                current = jobDefaultURL ? jobDefaultURL : MARK;
                break;
            default:
                current = MARK;
                break;
        }
        //返回判断值
        return current;
    };
    //首页选中
    Obj.firstLiCur = function () {
        $menu.find("li:first").addClass(_cur);
    };
    //不区分大小写的选中
    Obj.selectedCur = function () {
        $menuli.each(function () {
            var _href = $(this).children('a').attr("href").toLowerCase();
            var _href2 = _href.substring(_href.lastIndexOf("/") + 1);
            //判断地址是否一样 一样的话添加选中
            if (_href == current||(_href2 ==currentshort&&currentshort!='index.html') && _href2!='' ) {
                $(this).addClass(_cur);
                //这个return false 只是跳出each ,并不跳出此方法
                return false;
            } else if (typeof (current) == "number") {
                $menuli.eq(current).addClass(_cur);
                //这个return false 只是跳出each ,并不跳出此方法
                return false;
            }
        });
    };
    //文字形式导航的选择.jQuery的contains默认会把所有的匹配到文字的链接加上样式  所以还得循环判断
    Obj.selectedTxtCur = function () {
        $menuli.children("a").each(function () {
            var _txt = $.trim($(this).text());
            //一般面包屑导航的最后一个都是首页[或者说"项目名称"加首页],然后在选择的时候如果主导航只有个首页的话,就会先把主导航选中,所以这里判断一下
            if (_txt == txt && txt.indexOf("首页") == -1) {
                $(this).parent("li").addClass(_cur);
                //这个return false 只是跳出each ,并不跳出此方法
                return false;
            }
        });
        //返回jQuery对象
        return $menu.find("ul").eq(0).children("li." + _cur);
    };
    //判断是否有主导航选中
    Obj.hasCur = function () {
        var _hascur = $menu.find("ul").eq(0).children("li." + _cur).size();
        return _hascur;
    };

    //判断MARK,如果不存在 直接首页选中并返回程序
    if (typeof (MARK) == 'undefined') {
        Obj.firstLiCur();
        return false;
    }

    //判断面包屑导航是否存在
    if (!count) {
        //如果不存在直接判断MARK 和栏目 的默认选中链接
        current = Obj.getCurrentURL();
        //获取添加
        Obj.selectedCur();
    }
    //循环面包屑导航 倒序
    for (var i = count - 1; i >= 0; i--) {
        //取链接地址
        current = $info.eq(i).attr("href");
        //取文本
        var txt = $.trim($info.eq(i).text());
        //截取"/"后面的链接
        currentshort = current.substring(current.lastIndexOf("/") + 1).toLowerCase();
        //如果截取到是空的话,一般就是最后一次循环还没有匹配到主导航的样式
        if (current == "" || current == undefined) {
            //判断MARK
            current = Obj.getCurrentURL();
        }
        //主导航的匹配文字 [一般情况下是没有用的,有时候会碰到说是这个文字,但是链接确是另外一个,但是导航选中还是要加在文字上面]
        //比如 二级分类是成功案例,但是它下面还有一个三级分类是经典案例,主导航上的是二级分类确标着三级分类的链接,这个文字就有用了
        //况且这里还要先判断文字再判断链接
        var $t = Obj.selectedTxtCur();
        //var $t = $("div.menu a:contains('" + txt + "')");
        //最后一次循环txt是首页,往往主导航的第一个都是**首页,所以要判断一下
        //判断文字
        if ($t.size() && txt.indexOf("首页") == -1) {
            $t.parent("li").addClass(_cur);
            return false;
        } else {//判断链接
            Obj.selectedCur();
            //如果选中导航,则跳出循环
            if (Obj.hasCur()) { return false; }
        }
    }
    //如果都没有主导航选中,给MARK加链接 各栏目首页 主要是产品首页没有面包屑导航,没有办法判断
    if (!Obj.hasCur()) {
        current = MARK;
        Obj.selectedCur();
        //如果还没有主导航选中,给第一个加样式
        if (!Obj.hasCur()) {
            Obj.firstLiCur();
        }
    } else {
    }
});
(function(){
    leftNavFocus.init();
})();

/* ==========================================================================
   美尔健官网移动端交互增强逻辑 (全端通用)
   ========================================================================== */
$(function () {
    // 检测相对路径前缀
    var basePrefix = "./";
    var mobileCssLink = $("link[href*='mobile.css']").attr("href");
    if (mobileCssLink) {
        if (mobileCssLink.indexOf("../../") === 0) {
            basePrefix = "../../";
        } else if (mobileCssLink.indexOf("../") === 0) {
            basePrefix = "../";
        }
    }

    // 1. 过滤主导航中的二级子项 (带有 ├ 或 └ 的项目添加 is-sub-item 类名)
    var navItems = [];
    var currentGroup = null;

    $(".g_nav ul li").each(function () {
        var $li = $(this);
        var $a = $li.find("a");
        var text = $.trim($a.text());
        var href = $a.attr("href") || "#";
        var title = $a.attr("title") || text;

        if (text.indexOf("├") !== -1 || text.indexOf("└") !== -1 || text.indexOf("—") !== -1) {
            $li.addClass("is-sub-item").hide();
            var cleanSubText = text.replace(/[├└—\s]/g, "");
            if (currentGroup && currentGroup.children) {
                currentGroup.children.push({
                    text: cleanSubText,
                    href: href,
                    title: title
                });
            }
        } else {
            currentGroup = {
                text: text,
                href: href,
                title: title,
                isCur: $li.hasClass("cur"),
                children: []
            };
            navItems.push(currentGroup);
        }
    });

    // 2. 移动端 Header 增加操作栏 (语言切换 + 汉堡按钮)
    var $mTop = $(".m_top");
    if ($mTop.length && !$(".mobile-header-actions").length) {
        var $actions = $('<div class="mobile-header-actions"></div>');
        var $langSwitch = $(".lang-switch");
        if ($langSwitch.length) {
            $actions.append($langSwitch);
        }
        var $toggleBtn = $('<div class="mobile-nav-toggle" id="mobileNavToggle" title="打开菜单">☰</div>');
        $actions.append($toggleBtn);
        if ($mTop.find(".tlogo").length) {
            $mTop.find(".tlogo").after($actions);
        } else {
            $mTop.prepend($actions);
        }
    }

    // 3. 构建全屏抽屉菜单 (Drawer Menu)
    if (!$("#mobileDrawer").length) {
        var drawerHtml = '';
        drawerHtml += '<div class="mobile-drawer-overlay" id="mobileDrawerOverlay"></div>';
        drawerHtml += '<div class="mobile-drawer" id="mobileDrawer">';
        drawerHtml += '  <div class="mobile-drawer-header">';
        drawerHtml += '    <h3>美尔健生物</h3>';
        drawerHtml += '    <div class="mobile-drawer-close" id="mobileDrawerClose">✕</div>';
        drawerHtml += '  </div>';
        drawerHtml += '  <div class="mobile-drawer-body">';
        drawerHtml += '    <ul class="mobile-drawer-menu">';

        for (var i = 0; i < navItems.length; i++) {
            var item = navItems[i];
            drawerHtml += '      <li class="mobile-drawer-item">';
            drawerHtml += '        <a class="mobile-drawer-link' + (item.isCur ? ' active' : '') + '" href="' + item.href + '">';
            drawerHtml += '          <span>' + item.text + '</span>';
            if (item.children && item.children.length > 0) {
                drawerHtml += '          <span class="mobile-drawer-arrow" style="font-size:12px;color:#a0aec0;">▼</span>';
            }
            drawerHtml += '        </a>';

            if (item.children && item.children.length > 0) {
                drawerHtml += '        <ul class="mobile-drawer-submenu">';
                for (var j = 0; j < item.children.length; j++) {
                    var sub = item.children[j];
                    drawerHtml += '          <li><a href="' + sub.href + '">' + sub.text + '</a></li>';
                }
                drawerHtml += '        </ul>';
            }
            drawerHtml += '      </li>';
        }

        drawerHtml += '    </ul>';
        drawerHtml += '  </div>';
        drawerHtml += '  <div class="mobile-drawer-footer">';
        drawerHtml += '    <a href="tel:0755-82926499" class="mobile-drawer-tel">📞 电话咨询：0755-82926499</a>';
        drawerHtml += '    <a href="tel:186-9197-8530" class="mobile-drawer-tel" style="background:#2b6cb0;">📱 移动专线：186-9197-8530</a>';
        drawerHtml += '  </div>';
        drawerHtml += '</div>';

        $("body").append(drawerHtml);

        // 抽屉开关交互
        $(document).on("click", "#mobileNavToggle", function () {
            $("#mobileDrawerOverlay").addClass("active");
            $("#mobileDrawer").addClass("active");
            $("body").css("overflow", "hidden");
        });

        $(document).on("click", "#mobileDrawerClose, #mobileDrawerOverlay", function () {
            $("#mobileDrawerOverlay").removeClass("active");
            $("#mobileDrawer").removeClass("active");
            $("body").css("overflow", "");
        });
    }

    // 4. 构建移动端底部快捷触达工具条 (Bottom Bar) 与微信二维码弹窗
    if (!$("#mobileBottomBar").length) {
        var bottomBarHtml = '';
        bottomBarHtml += '<div class="mobile-bottom-bar" id="mobileBottomBar">';
        bottomBarHtml += '  <a href="tel:0755-82926499" class="mobile-bottom-bar-item">';
        bottomBarHtml += '    <span class="mobile-bottom-bar-icon">📞</span>';
        bottomBarHtml += '    <span>电话咨询</span>';
        bottomBarHtml += '  </a>';
        bottomBarHtml += '  <a href="javascript:void(0);" class="mobile-bottom-bar-item" id="mobileWxBtn">';
        bottomBarHtml += '    <span class="mobile-bottom-bar-icon">💬</span>';
        bottomBarHtml += '    <span>微信客服</span>';
        bottomBarHtml += '  </a>';
        bottomBarHtml += '  <a href="' + basePrefix + 'helps/lxwm.html" class="mobile-bottom-bar-item highlight">';
        bottomBarHtml += '    <span class="mobile-bottom-bar-icon">📋</span>';
        bottomBarHtml += '    <span>联系我们</span>';
        bottomBarHtml += '  </a>';
        bottomBarHtml += '  <a href="javascript:void(0);" class="mobile-bottom-bar-item" id="mobileBackTopBtn">';
        bottomBarHtml += '    <span class="mobile-bottom-bar-icon">🔝</span>';
        bottomBarHtml += '    <span>回到顶部</span>';
        bottomBarHtml += '  </a>';
        bottomBarHtml += '</div>';

        // 微信弹窗
        bottomBarHtml += '<div class="mobile-wx-modal" id="mobileWxModal">';
        bottomBarHtml += '  <div class="mobile-wx-modal-box">';
        bottomBarHtml += '    <div class="mobile-wx-modal-close" id="mobileWxModalClose">✕</div>';
        bottomBarHtml += '    <h4>微信客服咨询</h4>';
        bottomBarHtml += '    <img src="' + basePrefix + 'resource/images/98118d91c8d74d289a05f86fc2519ad7_6.jpg" alt="微信客服">';
        bottomBarHtml += '    <p>长按识别二维码或添加客服微信<br>为您提供一对一原料咨询与技术支持</p>';
        bottomBarHtml += '  </div>';
        bottomBarHtml += '</div>';

        $("body").append(bottomBarHtml);

        // 底部工具条事件
        $(document).on("click", "#mobileWxBtn", function () {
            $("#mobileWxModal").addClass("active");
        });

        $(document).on("click", "#mobileWxModalClose, #mobileWxModal", function (e) {
            if (e.target.id === 'mobileWxModal' || e.target.id === 'mobileWxModalClose') {
                $("#mobileWxModal").removeClass("active");
            }
        });

        $(document).on("click", "#mobileBackTopBtn", function () {
            $("html, body").animate({ scrollTop: 0 }, 300);
        });
    }

    // 5. 修复移动端选项卡点击交互 (解决方案、制造中心等在移动端触摸点击切换)
    $(".g_fa .fafl dl, .g_fa .dzoem").on("click", function () {
        $(this).addClass("cur").siblings().removeClass("cur");
    });

    $(".g_zzzx .tabsfa a").on("click", function (e) {
        e.preventDefault();
        var index = $(this).index();
        $(this).addClass("active").siblings().removeClass("active");
        var $slides = $(".g_zzzx .m_zzzx .swiper-slide");
        if ($slides.length) {
            $slides.hide().eq(index).show();
        }
    });

    $(".g_news .tabsnew a").on("click", function (e) {
        var index = $(this).index();
        $(this).addClass("active").siblings().removeClass("active");
        var $newsSlides = $(".g_news .m_news .swiper-slide");
        if ($newsSlides.length) {
            $newsSlides.hide().eq(index).show();
        }
    });

    // 6. 内页移动端横滑导航自动居中当前激活项 (Active Tab Auto Scroll)
    function autoScrollActiveTab() {
        var $activeTab = $(".p102-fdh-3 ul li.sidenavcur, .p102-fdh-3 ul li.cur, .p102-fdh-3 ul li.on, .p102-fdh-3 .content3 li.sidenavcur, .p102-fdh-3 .content3 li.cur, .p101a-fdh-02-nav ul li.cur");
        if ($activeTab.length) {
            var $parent = $activeTab.parent();
            var offsetLeft = $activeTab.position().left;
            var parentScroll = $parent.scrollLeft();
            var parentWidth = $parent.width();
            var tabWidth = $activeTab.outerWidth();
            $parent.animate({
                scrollLeft: parentScroll + offsetLeft - (parentWidth / 2) + (tabWidth / 2)
            }, 300);
        }
    }
    setTimeout(autoScrollActiveTab, 150);

    // 7. 产品列表分类轻量折叠手风琴效果
    if ($(window).width() <= 768) {
        $(".p102-fdh-1-nav-one h3").on("click", function () {
            var $dl = $(this).siblings("dl");
            $dl.slideToggle(200);
        });
    }

    // 8. 修复内页 Banner 图片被特定内联脚本偏移撑裂的问题
    function fixMobileBanners() {
        if ($(window).width() <= 768) {
            $(".ty-banner-1").each(function () {
                var $ban = $(this);
                var $img = $ban.find("img");
                $img.removeAttr("style").css({
                    "width": "100%",
                    "height": "100%",
                    "margin-left": "0",
                    "position": "relative",
                    "left": "0",
                    "display": "block",
                    "visibility": "visible"
                });
                $ban.css({
                    "height": "140px",
                    "min-height": "120px",
                    "max-height": "180px",
                    "overflow": "hidden"
                });
            });
        }
    }
    fixMobileBanners();
    $(window).on("load resize", fixMobileBanners);
    setTimeout(fixMobileBanners, 200);
    setTimeout(fixMobileBanners, 600);
});

// 9. 全站受访页面、产品点击与停留时间智能追踪探针 (Mellgen Smart Visitor Tracker)
(function() {
    try {
        var protocol = window.location.protocol;
        var hostname = window.location.hostname;
        var pathname = window.location.pathname || "";
        var cleanPath = pathname.replace(/^\/+/, "");
        if (!cleanPath) cleanPath = "index.html";

        var pageTitle = document.title || "美尔健官方页面";
        var pageType = "页面浏览";
        if (cleanPath.indexOf("products/") !== -1 || cleanPath.indexOf("product_") !== -1) {
            pageType = "产品详情";
        } else if (cleanPath.indexOf("articles/") !== -1 || cleanPath.indexOf("article_") !== -1) {
            pageType = "资讯文章";
        } else if (cleanPath === "index.html") {
            pageType = "官网首页";
        }

        var referrer = document.referrer || "直接访问";
        var apiUrl = protocol + "//" + hostname + ":8001/api/analytics/track_pageview";

        var startTime = Date.now();

        function sendPing(isInitial) {
            var elapsed = Math.floor((Date.now() - startTime) / 1000);
            var payload = JSON.stringify({
                url: cleanPath,
                title: pageTitle,
                type: pageType,
                duration: elapsed,
                referrer: referrer,
                initial: !!isInitial
            });

            if (navigator.sendBeacon) {
                var blob = new Blob([payload], { type: "application/json" });
                navigator.sendBeacon(apiUrl, blob);
            } else {
                var xhr = new XMLHttpRequest();
                xhr.open("POST", apiUrl, true);
                xhr.setRequestHeader("Content-Type", "application/json");
                xhr.send(payload);
            }
        }

        // 1. Initial pageview ping
        sendPing(true);

        // 2. Heartbeat every 15s to track stay duration
        setInterval(function() {
            sendPing(false);
        }, 15000);

        // 3. Final duration ping on leave/tab hide
        window.addEventListener("beforeunload", function() {
            sendPing(false);
        });
        document.addEventListener("visibilitychange", function() {
            if (document.visibilityState === "hidden") {
                sendPing(false);
            }
        });
    } catch(e) {}
})();

