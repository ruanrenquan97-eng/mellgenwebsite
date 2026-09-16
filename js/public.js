/*&中文2017-01-05姜玮111&*/
//副导航焦点定位
var leftNavFocus = {
    init: function() {
        if (typeof $ === 'undefined') return;
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
if (typeof $ !== 'undefined') {
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
}
(function(){
    try {
        if (typeof leftNavFocus !== 'undefined') {
            leftNavFocus.init();
        }
    } catch(e){}
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

    // 2. 移动端 Header 增加操作栏 (仅保留语言切换，按需移除右上角汉堡导航)
    var $mTop = $(".m_top");
    if ($mTop.length && !$(".mobile-header-actions").length) {
        var $actions = $('<div class="mobile-header-actions"></div>');
        var $langSwitch = $(".lang-switch");
        if ($langSwitch.length) {
            $actions.append($langSwitch);
        }
        // 右上角汉堡导航按钮已按需求彻底移除
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

        var isEn = (window.location.pathname || "").indexOf("/en/") !== -1 || (document.documentElement.lang || "").toLowerCase().indexOf("en") !== -1;
        for (var i = 0; i < navItems.length; i++) {
            var item = navItems[i];
            var hasChildren = item.children && item.children.length > 0;
            drawerHtml += '      <li class="mobile-drawer-item' + (hasChildren ? ' has-children' : '') + '">';
            drawerHtml += '        <div class="mobile-drawer-link-wrap">';
            drawerHtml += '          <a class="mobile-drawer-link' + (item.isCur ? ' active' : '') + '" href="' + item.href + '">';
            drawerHtml += '            <span>' + item.text + '</span>';
            drawerHtml += '          </a>';
            if (hasChildren) {
                drawerHtml += '          <button type="button" class="mobile-drawer-toggle" aria-label="展开子菜单" title="展开/收起">';
                drawerHtml += '            <svg class="mobile-drawer-arrow" viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"></polyline></svg>';
                drawerHtml += '          </button>';
            }
            drawerHtml += '        </div>';

            if (hasChildren) {
                // 默认不展开：设置 style="display: none;"
                drawerHtml += '        <ul class="mobile-drawer-submenu" style="display: none;">';
                var allLabel = isEn ? ('View All ' + item.text + ' →') : ('查看全部 ' + item.text + ' →');
                drawerHtml += '          <li class="mobile-drawer-sub-all"><a href="' + item.href + '">' + allLabel + '</a></li>';
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
        drawerHtml += '    <a href="tel:136-9197-8530" class="mobile-drawer-tel" style="background:#2b6cb0;">📱 移动专线：136-9197-8530</a>';
        drawerHtml += '  </div>';
        drawerHtml += '</div>';

        $("body").append(drawerHtml);

        // 抽屉子菜单折叠/展开交互 (默认全部收起，点击展开/收起)
        $(document).on("click", ".mobile-drawer-toggle", function (e) {
            e.preventDefault();
            e.stopPropagation();
            var $item = $(this).closest(".mobile-drawer-item");
            var $submenu = $item.find("> .mobile-drawer-submenu");
            var isOpen = $item.hasClass("is-open");
            
            if (isOpen) {
                $submenu.slideUp(200);
                $item.removeClass("is-open");
            } else {
                $submenu.slideDown(200);
                $item.addClass("is-open");
            }
        });

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

    // 4. 构建移动端底部快捷触达工具条 (Bottom Bar) - 整合首页、全站导航、AI客服与回到顶部
    if (!$("#mobileBottomBar").length) {
        var isEn = (window.location.pathname || "").indexOf("/en/") !== -1 || (document.documentElement.lang || "").toLowerCase().indexOf("en") !== -1;
        var currentPath = window.location.pathname || "";
        var isHome = currentPath.endsWith("index.html") || currentPath === "/" || currentPath.endsWith("/");

        var homeUrl = isEn ? (currentPath.indexOf("/en/") !== -1 ? (basePrefix === "../" ? "./index.html" : (basePrefix === "../../" ? "../index.html" : "./index.html")) : basePrefix + "en/index.html") : basePrefix + "index.html";

        var bottomBarHtml = '';
        bottomBarHtml += '<div class="mobile-bottom-bar" id="mobileBottomBar">';
        bottomBarHtml += '  <a href="' + homeUrl + '" class="mobile-bottom-bar-item' + (isHome ? ' active' : '') + '" id="mobileHomeBtn">';
        bottomBarHtml += '    <span class="mobile-bottom-bar-icon">🏠</span>';
        bottomBarHtml += '    <span>' + (isEn ? "Home" : "首页") + '</span>';
        bottomBarHtml += '  </a>';
        bottomBarHtml += '  <a href="javascript:void(0);" class="mobile-bottom-bar-item" id="mobileNavBtn">';
        bottomBarHtml += '    <span class="mobile-bottom-bar-icon">☰</span>';
        bottomBarHtml += '    <span>' + (isEn ? "Menu" : "导航") + '</span>';
        bottomBarHtml += '  </a>';
        bottomBarHtml += '  <a href="javascript:void(0);" class="mobile-bottom-bar-item highlight" id="mobileAiBtn">';
        bottomBarHtml += '    <span class="mobile-bottom-bar-icon">🤖</span>';
        bottomBarHtml += '    <span>' + (isEn ? "AI Support" : "AI客服") + '</span>';
        bottomBarHtml += '  </a>';
        bottomBarHtml += '  <a href="javascript:void(0);" class="mobile-bottom-bar-item" id="mobileBackTopBtn">';
        bottomBarHtml += '    <span class="mobile-bottom-bar-icon">🔝</span>';
        bottomBarHtml += '    <span>' + (isEn ? "Top" : "回到顶部") + '</span>';
        bottomBarHtml += '  </a>';
        bottomBarHtml += '</div>';

        $("body").append(bottomBarHtml);

        // 底部工具条事件 - 唤起AI智能客服
        $(document).on("click", "#mobileAiBtn", function () {
            if (window.MellgenAIChat) {
                window.MellgenAIChat.open();
            } else {
                var t = document.getElementById("mg-ai-trigger");
                if (t) t.click();
            }
        });

        // 底部工具条事件 - 快捷打开/关闭全站导航抽屉
        $(document).on("click", "#mobileNavBtn", function (e) {
            e.preventDefault();
            if ($("#mobileDrawer").hasClass("active")) {
                $("#mobileDrawerOverlay").removeClass("active");
                $("#mobileDrawer").removeClass("active");
                $("body").css("overflow", "");
            } else {
                $("#mobileDrawerOverlay").addClass("active");
                $("#mobileDrawer").addClass("active");
                $("body").css("overflow", "hidden");
            }
        });

        $(document).on("click", "#mobileBackTopBtn", function () {
            $("html, body").animate({ scrollTop: 0 }, 300);
        });
    }

    // 5. 优化移动端选项卡点击交互 (解决方案、制造中心等在移动端触摸点击切换)
    $(document).on("click touchend", ".g_fa .fafl dl", function () {
        var $this = $(this);
        var idx = $this.index();
        $this.addClass("cur").siblings("dl").removeClass("cur");
        var swiperContainer = document.querySelector('.g_fa .faright .js-swiper-tab');
        if (swiperContainer && swiperContainer.swiper) {
            swiperContainer.swiper.slideTo(idx);
        } else {
            $this.trigger('mouseover');
        }
    });

    $(document).on("click touchend", ".g_fa .dzoem", function () {
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

    // 5. 移动端防跳出优化：移除站内链接上的 target="_blank"，防止在新标签页打开时浏览器退回到电脑端视图
    function fixMobileLinkTargets() {
        if ($(window).width() <= 768 || ('ontouchstart' in window)) {
            $("a[target='_blank']").each(function () {
                var href = $(this).attr("href") || "";
                if (href.indexOf("://") === -1 || href.indexOf("mellgen.com") !== -1 || href.indexOf("localhost") !== -1 || href.indexOf("127.0.0.1") !== -1) {
                    $(this).removeAttr("target");
                }
            });
        }
    }
    fixMobileLinkTargets();
    setTimeout(fixMobileLinkTargets, 300);

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

    // 8. 解决内页 Banner 图片被特定内联脚本偏移撑裂的问题
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
        // 环境自适应：本地预览端口 8000 时走 8001；在生产环境 (https://www.mellgen.com) 或直接访问后台时走同源 /api/...
        var apiUrl = "/api/analytics/track_pageview";
        if (window.location.port === "8000" && (hostname === "localhost" || hostname === "127.0.0.1")) {
            apiUrl = protocol + "//" + hostname + ":8001/api/analytics/track_pageview";
        }

        var startTime = Date.now();

        // 识别访客设备端：手机端 vs 电脑端
        var isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini|Mobile/i.test(navigator.userAgent || "") ||
                       (window.innerWidth && window.innerWidth <= 768) ||
                       (navigator.maxTouchPoints && navigator.maxTouchPoints > 1 && window.innerWidth < 1024);
        var clientDevice = isMobile ? "手机端" : "电脑端";

        function sendPing(isInitial) {
            var elapsed = Math.floor((Date.now() - startTime) / 1000);
            var payload = JSON.stringify({
                url: cleanPath,
                title: pageTitle,
                type: pageType,
                duration: elapsed,
                referrer: referrer,
                device: clientDevice,
                initial: !!isInitial
            });

            if (!isInitial && navigator.sendBeacon) {
                try {
                    var blob = new Blob([payload], { type: "application/json" });
                    navigator.sendBeacon(apiUrl, blob);
                    return;
                } catch(e) {}
            }
            if (window.fetch) {
                fetch(apiUrl, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: payload,
                    keepalive: true
                }).catch(function() {});
            } else {
                try {
                    var xhr = new XMLHttpRequest();
                    xhr.open("POST", apiUrl, true);
                    xhr.setRequestHeader("Content-Type", "application/json");
                    xhr.send(payload);
                } catch(e) {}
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

// 彻底清理旧版右侧客服侧栏 (#client-2112 等)，仅保留右下角AI在线客服“小美”
(function() {
    try {
        function purgeLegacySidebar() {
            var sels = ["#client-2112", ".xin-2112-client-1", ".my-kefu", ".client-2112-cont", ".client-2112-cont-weixin"];
            sels.forEach(function(s) {
                var items = document.querySelectorAll(s);
                items.forEach(function(el) {
                    if (el && el.parentNode) el.parentNode.removeChild(el);
                });
            });
        }
        purgeLegacySidebar();
        if (document.readyState === "loading") {
            document.addEventListener("DOMContentLoaded", purgeLegacySidebar);
        }
        setTimeout(purgeLegacySidebar, 200);
        setTimeout(purgeLegacySidebar, 1000);
    } catch(e) {}
})();

// 全局加载美尔健 AI 智能客服挂件（小美客服）
(function() {
    try {
        function injectAIChatWidget() {
            if (document.getElementById("mg-ai-chat-script")) return;
            var script = document.createElement("script");
            script.id = "mg-ai-chat-script";

            // 动态根据 public.js 所在路径精准定位 js/ai_chat_widget.js
            var prefix = "";
            var scripts = document.getElementsByTagName("script");
            for (var i = 0; i < scripts.length; i++) {
                var src = scripts[i].getAttribute("src") || scripts[i].src || "";
                if (src.indexOf("public.js") !== -1) {
                    var idx = src.indexOf("public.js");
                    prefix = src.substring(0, idx);
                    break;
                }
            }
            if (!prefix) {
                var clean = (window.location.pathname || "").replace(/^\/+/, "");
                var parts = clean.split("/").filter(function(p){ return p.length > 0; });
                if (parts.length > 1) {
                    var depth = parts.length - 1;
                    for (var d = 0; d < depth; d++) prefix += "../";
                    prefix += "js/";
                } else {
                    prefix = "./js/";
                }
            }
            script.src = prefix + "ai_chat_widget.js?v=20260912_v11";
            script.async = true;
            if (document.body) {
                document.body.appendChild(script);
            } else {
                document.head.appendChild(script);
            }
        }
        if (document.readyState === "loading") {
            document.addEventListener("DOMContentLoaded", injectAIChatWidget);
        } else {
            injectAIChatWidget();
        }
    } catch(e) {}
})();

// 独立的移动端底部快捷触达工具条自动兜底保证 (Vanilla JS 零依赖，永不失效)
(function ensureMobileBottomBarVanilla() {
    function injectBar() {
        if (document.getElementById("mobileBottomBar")) return;
        if (!document.body) return;

        var isEn = (window.location.pathname || "").indexOf("/en/") !== -1 || (document.documentElement.lang || "").toLowerCase().indexOf("en") !== -1;
        var currentPath = window.location.pathname || "";
        var isHome = currentPath.endsWith("index.html") || currentPath === "/" || currentPath.endsWith("/");

        var basePrefix = "./";
        var mobileCssLink = document.querySelector("link[href*='mobile.css']");
        if (mobileCssLink) {
            var href = mobileCssLink.getAttribute("href") || "";
            if (href.indexOf("../../") === 0) basePrefix = "../../";
            else if (href.indexOf("../") === 0) basePrefix = "../";
        }

        var homeUrl = isEn ? (currentPath.indexOf("/en/") !== -1 ? (basePrefix === "../" ? "./index.html" : (basePrefix === "../../" ? "../index.html" : "./index.html")) : basePrefix + "en/index.html") : basePrefix + "index.html";

        var bar = document.createElement("div");
        bar.className = "mobile-bottom-bar";
        bar.id = "mobileBottomBar";
        bar.innerHTML = [
            '  <a href="' + homeUrl + '" class="mobile-bottom-bar-item' + (isHome ? ' active' : '') + '" id="mobileHomeBtn">',
            '    <span class="mobile-bottom-bar-icon">🏠</span>',
            '    <span>' + (isEn ? "Home" : "首页") + '</span>',
            '  </a>',
            '  <a href="javascript:void(0);" class="mobile-bottom-bar-item" id="mobileNavBtn">',
            '    <span class="mobile-bottom-bar-icon">☰</span>',
            '    <span>' + (isEn ? "Menu" : "导航") + '</span>',
            '  </a>',
            '  <a href="javascript:void(0);" class="mobile-bottom-bar-item highlight" id="mobileAiBtn">',
            '    <span class="mobile-bottom-bar-icon">🤖</span>',
            '    <span>' + (isEn ? "AI Support" : "AI客服") + '</span>',
            '  </a>',
            '  <a href="javascript:void(0);" class="mobile-bottom-bar-item" id="mobileBackTopBtn">',
            '    <span class="mobile-bottom-bar-icon">🔝</span>',
            '    <span>' + (isEn ? "Top" : "回到顶部") + '</span>',
            '  </a>'
        ].join("");

        document.body.appendChild(bar);

        bar.addEventListener("click", function(e) {
            var target = e.target.closest("a");
            if (!target) return;
            if (target.id === "mobileAiBtn") {
                e.preventDefault();
                if (window.MellgenAIChat) {
                    window.MellgenAIChat.open();
                } else {
                    var t = document.getElementById("mg-ai-trigger");
                    if (t) t.click();
                }
            } else if (target.id === "mobileNavBtn") {
                e.preventDefault();
                var drawer = document.getElementById("mobileDrawer");
                var overlay = document.getElementById("mobileDrawerOverlay");
                if (drawer && overlay) {
                    if (drawer.classList.contains("active")) {
                        drawer.classList.remove("active");
                        overlay.classList.remove("active");
                        document.body.style.overflow = "";
                    } else {
                        drawer.classList.add("active");
                        overlay.classList.add("active");
                        document.body.style.overflow = "hidden";
                    }
                }
            } else if (target.id === "mobileBackTopBtn") {
                e.preventDefault();
                window.scrollTo({ top: 0, behavior: "smooth" });
            }
        });
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", injectBar);
    } else {
        injectBar();
    }
    setTimeout(injectBar, 300);
})();

// 移动端页脚导航扁平化重构，确保移动端排成整齐的两行（第一行4个，第二行3个），桌面端保持完整原始列表
(function () {
    function flattenMobileFooterNav() {
        var ftnav = document.querySelector(".g_ft .ftmid .ftnav");
        if (!ftnav) return;

        // 仅在移动端屏幕 (<= 768px) 下执行！在桌面端必须完整保留 3 列导航，绝对不可隐藏 dl！
        if (window.innerWidth > 768) {
            var oldFlat = ftnav.querySelector(".m-ftnav-flat");
            if (oldFlat) {
                oldFlat.parentNode.removeChild(oldFlat);
            }
            var origDls = ftnav.querySelectorAll("dl");
            for (var k = 0; k < origDls.length; k++) {
                origDls[k].style.removeProperty("display");
            }
            ftnav.removeAttribute("data-flattened");
            return;
        }

        if (ftnav.getAttribute("data-flattened") === "true") return;

        var links = [];
        // 1. 快捷链接列表 (解决方案、透皮肽技术、联系我们、关于我们、视频中心)
        var dl1 = ftnav.querySelector("dl:nth-child(1)");
        if (dl1) {
            var ddLinks = dl1.querySelectorAll("dd a");
            for (var i = 0; i < ddLinks.length; i++) {
                links.push(ddLinks[i]);
            }
        }
        // 2. 产品中心
        var dl2 = ftnav.querySelector("dl:nth-child(2)");
        if (dl2) {
            var dtLink = dl2.querySelector("dt a");
            if (dtLink) links.push(dtLink);
        }
        // 3. 行业案例
        var dl3 = ftnav.querySelector("dl:nth-child(3)");
        if (dl3) {
            var dtLink = dl3.querySelector("dt a");
            if (dtLink) links.push(dtLink);
        }

        if (links.length >= 4) {
            var oldFlats = ftnav.querySelectorAll(".m-ftnav-flat");
            for (var m = 0; m < oldFlats.length; m++) {
                oldFlats[m].parentNode.removeChild(oldFlats[m]);
            }

            var flat = document.createElement("div");
            flat.className = "m-ftnav-flat";

            var row1 = document.createElement("div");
            row1.className = "m-ftnav-row m-ftnav-row1";
            for (var i = 0; i < Math.min(4, links.length); i++) {
                row1.appendChild(links[i].cloneNode(true));
            }
            flat.appendChild(row1);

            if (links.length > 4) {
                var row2 = document.createElement("div");
                row2.className = "m-ftnav-row m-ftnav-row2";
                for (var j = 4; j < links.length; j++) {
                    row2.appendChild(links[j].cloneNode(true));
                }
                flat.appendChild(row2);
            }

            // 移动端隐藏原始的所有 dl 节点，防止文字在上方重复出现
            var dls = ftnav.querySelectorAll("dl");
            for (var k = 0; k < dls.length; k++) {
                dls[k].style.setProperty("display", "none", "important");
            }

            ftnav.appendChild(flat);
            ftnav.setAttribute("data-flattened", "true");
        }
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", flattenMobileFooterNav);
    } else {
        flattenMobileFooterNav();
    }
    setTimeout(flattenMobileFooterNav, 200);
    window.addEventListener("resize", flattenMobileFooterNav);
})();

// 视频中心海报自动注入与智能弹窗播放器（解决移动端黑屏、封面丢失与多端播放体验）
(function() {
    function initVideoInteractive() {
        if (typeof $ === 'undefined') return;
        var $videoList = $('.zxlb-3n-ts-02-list dl');
        if (!$videoList.length) return;

        $videoList.each(function() {
            var $dl = $(this);
            var $video = $dl.find('video');
            var $img = $dl.find('dt i img');
            if ($video.length && $img.length) {
                var imgSrc = $img.attr('src');
                if (imgSrc && !$video.attr('poster')) {
                    $video.attr('poster', imgSrc);
                }
            }

            // Bind click to open video modal player
            if (!$dl.data('video-modal-bound')) {
                $dl.data('video-modal-bound', true);
                $dl.css('cursor', 'pointer');
                $dl.on('click', function(e) {
                    if (e.target && e.target.tagName === 'VIDEO' && e.target.controls) {
                        return;
                    }
                    var videoSrc = $video.attr('src') || $dl.attr('data-video-src');
                    var videoTitle = $dl.find('dd h4 b').text().trim() || $img.attr('alt') || '美尔健官方视频';
                    if (videoSrc) {
                        e.preventDefault();
                        openGlobalVideoModal(videoSrc, videoTitle);
                    }
                });
            }
        });
    }

    function openGlobalVideoModal(src, title) {
        var modalId = 'mellgen-global-video-modal';
        var $modal = $('#' + modalId);
        if (!$modal.length) {
            $('body').append(
                '<div id="' + modalId + '" style="display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(15,23,42,0.88);backdrop-filter:blur(6px);z-index:999999;align-items:center;justify-content:center;padding:16px;box-sizing:border-box;">' +
                  '<div style="background:#0f172a;border:1px solid rgba(255,255,255,0.15);border-radius:16px;max-width:920px;width:100%;overflow:hidden;box-shadow:0 25px 50px -12px rgba(0,0,0,0.6);display:flex;flex-direction:column;">' +
                    '<div style="display:flex;align-items:center;justify-content:space-between;padding:14px 20px;border-bottom:1px solid rgba(255,255,255,0.1);color:#ffffff;">' +
                      '<span id="' + modalId + '-title" style="font-size:14px;font-weight:bold;flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;"></span>' +
                      '<button id="' + modalId + '-close" style="background:transparent;border:none;color:#94a3b8;font-size:24px;cursor:pointer;line-height:1;padding:0 6px;margin-left:12px;" title="关闭">&times;</button>' +
                    '</div>' +
                    '<div style="background:#000;position:relative;padding-top:56.25%;height:0;overflow:hidden;">' +
                      '<video id="' + modalId + '-player" controls autoplay playsinline style="position:absolute;top:0;left:0;width:100%;height:100%;object-fit:contain;background:#000;"></video>' +
                    '</div>' +
                  '</div>' +
                '</div>'
            );
            $modal = $('#' + modalId);
            $('#' + modalId + '-close').on('click', closeGlobalVideoModal);
            $modal.on('click', function(e) {
                if (e.target.id === modalId) {
                    closeGlobalVideoModal();
                }
            });
            $(document).on('keydown', function(e) {
                if (e.key === 'Escape' && $modal.is(':visible')) {
                    closeGlobalVideoModal();
                }
            });
        }

        $('#' + modalId + '-title').text(title);
        var player = document.getElementById(modalId + '-player');
        if (player) {
            player.src = src;
            player.play().catch(function() {});
        }
        $modal.css('display', 'flex').hide().fadeIn(200);
    }

    function closeGlobalVideoModal() {
        var modalId = 'mellgen-global-video-modal';
        var $modal = $('#' + modalId);
        var player = document.getElementById(modalId + '-player');
        if (player) {
            player.pause();
            player.src = '';
        }
        if ($modal.length) {
            $modal.fadeOut(150);
        }
    }

    window.openGlobalVideoModal = openGlobalVideoModal;
    window.closeGlobalVideoModal = closeGlobalVideoModal;

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initVideoInteractive);
    } else {
        initVideoInteractive();
    }
    setTimeout(initVideoInteractive, 300);
})();

// ==============================================================================
// 10. 全球访客地域智能语言路由 (GeoIP Auto Language Switcher)
// 规则：
// 1. 中国大陆 (CN)、中国香港 (HK)、中国澳门 (MO)、中国台湾 (TW) 及本地/内网访客默认显示中文版本；
// 2. 其余所有非中国地区的海外 IP 访问中文页面时，自动引导平滑重定向至对应的 /en/ 英文版本；
// 3. 用户在页面顶部主动点击 CN/EN 或携带 ?lang=zh 参数时，优先尊重用户选择，避免死循环。
// ==============================================================================
(function() {
    try {
        var pathname = window.location.pathname || "";
        // 排除后台管理与鉴权路径
        if (pathname.indexOf("/dashboard") !== -1 || pathname.indexOf("/login") !== -1 || pathname.indexOf("/admin") !== -1) {
            return;
        }

        // 1. 监听全站导航中英文语言切换按钮点击事件，记录用户主动选择
        document.addEventListener("click", function(e) {
            var target = e.target && e.target.closest("a");
            if (!target) return;
            var href = target.getAttribute("href") || "";
            var title = target.getAttribute("title") || "";
            var text = (target.textContent || "").trim();

            if (title.indexOf("Chinese") !== -1 || text === "CN" || (href.indexOf("index.html") !== -1 && href.indexOf("/en/") === -1 && pathname.indexOf("/en/") !== -1)) {
                localStorage.setItem("mellgen_lang_pref", "zh");
            } else if (title.indexOf("English") !== -1 || text === "EN" || href.indexOf("/en/") !== -1) {
                localStorage.setItem("mellgen_lang_pref", "en");
            }
        });

        // 2. 支持 URL 显式参数强行指定语言（如 ?lang=zh）
        var search = window.location.search || "";
        if (search.indexOf("lang=zh") !== -1) {
            localStorage.setItem("mellgen_lang_pref", "zh");
            return;
        } else if (search.indexOf("lang=en") !== -1) {
            localStorage.setItem("mellgen_lang_pref", "en");
        }

        var isEnPage = pathname.indexOf("/en/") !== -1;
        var userPref = localStorage.getItem("mellgen_lang_pref");

        // 若用户主动选择过中文，哪怕身处海外也尊重选择，不再跳转
        if (userPref === "zh") {
            return;
        }

        // 当前已在英文页面，无需执行重定向
        if (isEnPage) {
            return;
        }

        // 3. 检查会话缓存，避免站内多次翻页重复发起网络探测
        var cachedLang = sessionStorage.getItem("mellgen_detected_lang");
        if (cachedLang) {
            if (cachedLang === "en") {
                redirectToEnPage();
            }
            return;
        }

        // 4. 重定向至对应英文版本页面
        function redirectToEnPage() {
            var currentPath = window.location.pathname.replace(/^\/+/, "");
            var targetEnUrl = "/en/index.html";
            if (!currentPath || currentPath === "index.html" || currentPath === "mellgen_home.html") {
                targetEnUrl = "/en/index.html";
            } else {
                targetEnUrl = "/en/" + currentPath;
            }
            if (window.location.search) targetEnUrl += window.location.search;
            if (window.location.hash) targetEnUrl += window.location.hash;
            window.location.replace(targetEnUrl);
        }

        function handleGeoResult(isChineseRegion) {
            if (isChineseRegion) {
                sessionStorage.setItem("mellgen_detected_lang", "zh");
            } else {
                sessionStorage.setItem("mellgen_detected_lang", "en");
                redirectToEnPage();
            }
        }

        // 5. 优先调用自有后端 /api/geo/lang 检测客户端真实公网 IP
        var apiUrl = "/api/geo/lang";
        if (window.location.port === "8000" && (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1")) {
            apiUrl = window.location.protocol + "//" + window.location.hostname + ":8001/api/geo/lang";
        }

        if (window.fetch) {
            fetch(apiUrl)
                .then(function(res) {
                    if (!res.ok) throw new Error("HTTP " + res.status);
                    return res.json();
                })
                .then(function(data) {
                    var isCn = data && (data.is_chinese_region === true || data.preferred_lang === "zh");
                    handleGeoResult(isCn);
                })
                .catch(function() {
                    // 若自有接口未响应，降级调用公网高可用快速 GeoIP 接口
                    fetch("https://ipwho.is/")
                        .then(function(res) { return res.json(); })
                        .then(function(geo) {
                            var code = (geo.country_code || "").toUpperCase();
                            var isCn = ["CN", "HK", "MO", "TW"].indexOf(code) !== -1;
                            handleGeoResult(isCn);
                        })
                        .catch(function() {
                            // 若所有探测均不可达，默认保持中文
                            sessionStorage.setItem("mellgen_detected_lang", "zh");
                        });
                });
        }
    } catch(e) {}
})();
