
(function() {
  'use strict';

  if (window.__MG_AI_CHAT_INITIALIZED__) return;
  window.__MG_AI_CHAT_INITIALIZED__ = true;

  function getApiBaseUrl() {
    var port = window.location.port;
    var host = window.location.hostname;
    var proto = window.location.protocol;
    if (port === "8000" && (host === "localhost" || host === "127.0.0.1")) {
      return proto + "//" + host + ":8001";
    }
    return "";
  }

  var API_BASE = getApiBaseUrl();
  var CHAT_ENDPOINT = API_BASE + "/api/ai_chat";
  var CONFIG_ENDPOINT = API_BASE + "/api/ai_service/config";

  var sessionId = "sess_" + Math.random().toString(36).substring(2, 9) + "_" + Date.now();
  var chatHistory = [];
  var isWaiting = false;
  var isOpen = false;
  var userQuestionCount = 0;

  var isEn = (window.location.pathname || "").indexOf("/en/") !== -1 || (document.documentElement.lang || "").toLowerCase().indexOf("en") !== -1;

  var aiConfig = {
    service_name: isEn ? "Mellgen AI Support" : "Mellgen AI Support",
    welcome_message: isEn 
      ? "Hello! I am Mellgen AI Consultant. We specialize in recombinant collagen, transdermal cyclic peptides, fibronectin, and PDRN. How can I assist you with raw materials, specs, or solutions today?"
      : "Hello! I am Mellgen Biotech's official AI consultant. We specialize in recombinant collagen, recombinant fibronectin, transdermal cyclic peptides, PDRN, and high-end bio-raw materials. How may I assist you today?",
    default_phones: ["136-9197-8530", "0755-82926499"],
    wechat_qrcode_url: "./resource/images/98118d91c8d74d289a05f86fc2519ad7_6.jpg",
    preset_questions: isEn ? [
      "What are the specifications of Recombinant Collagen?",
      "Can you provide TDS/COA for Transdermal Fibronectin?",
      "What is the MOQ and how to request samples?",
      "How many patents does Mellgen hold?",
      "Connect with Account Manager"
    ] : [
      "What specifications and grades are available for recombinant collagen?",
      "Can you provide COA and testing reports for transdermal fibronectin?",
      "What is the MOQ? How can I request free testing samples?",
      "How many core invention patents does Mellgen hold?",
      "Connect with Account Manager & Tech Support"
    ]
  };

  function removeOldSidebar() {
    var selectors = [
      "#client-2112",
      ".xin-2112-client-1",
      ".my-kefu",
      ".client-2112-cont",
      ".client-2112-cont-weixin",
      "[id^='client-2112']",
      "[class*='xin-2112']"
    ];
    selectors.forEach(function(sel) {
      try {
        var elements = document.querySelectorAll(sel);
        elements.forEach(function(el) {
          if (el && el.parentNode) {
            el.parentNode.removeChild(el);
          }
        });
      } catch(e) {}
    });
  }

  function createWidgetDOM() {
    removeOldSidebar();

    var trigger = document.createElement("div");
    trigger.id = "mg-ai-trigger";
    trigger.style.cssText = "position:fixed;bottom:30px;right:28px;height:52px;padding:0 20px 0 16px;border-radius:26px;background:linear-gradient(135deg,#10b981 0%,#047857 100%);box-shadow:0 8px 24px rgba(5,150,105,0.4);cursor:pointer;z-index:99998;display:flex;align-items:center;gap:10px;user-select:none;color:#fff;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Segoe UI',sans-serif;";
    trigger.setAttribute("title", isEn ? "Click to chat with AI Support (Online)" : "AI (AI)");
    trigger.innerHTML = 
      '<svg class="mg-ai-icon" viewBox="0 0 24 24" style="width:24px;height:24px;fill:currentColor;flex-shrink:0;">' +
        '<path d="M12 2C6.48 2 2 6.48 2 12c0 1.82.49 3.53 1.34 5L2 22l5.2-1.3c1.43.76 3.05 1.3 4.8 1.3 5.52 0 10-4.48 10-10S17.52 2 12 2zm1 14h-2v-2h2v2zm0-4h-2V7h2v5z"/>' +
      '</svg>' +
      '<span class="mg-ai-btn-text" style="font-size:15px;font-weight:700;letter-spacing:0.5px;white-space:nowrap;color:#fff;">' + (isEn ? "AI Support" : "AI") + '</span>' +
      '<span class="mg-ai-badge" style="background:#ffffff;color:#047857;font-size:11px;font-weight:700;padding:2px 8px;border-radius:10px;white-space:nowrap;box-shadow:0 1px 3px rgba(0,0,0,0.1);">' + (isEn ? "Online" : "AI") + '</span>';

    var hint = document.createElement("div");
    hint.id = "mg-ai-bubble-hint";
    hint.innerHTML = 
      '<div style="font-weight:600; color:#059669; font-size:13px; display:flex; align-items:center; gap:5px; margin-bottom:1px;">' +
        '<span style="display:inline-block; width:6px; height:6px; background:#10b981; border-radius:50%; flex-shrink:0;"></span>' +
        '<span>' + (isEn ? "Mellgen AI Support" : "AI · ") + '</span>' +
      '</div>' +
      '<div style="font-size:12.5px; color:#374151; line-height:1.45;">' + (isEn ? "Hello! Ask me about raw material specs, COA, or turnkey formulas." : "！AI，、COA~") + '</div>' +
      '<span class="mg-hint-close" title="Close hint">&times;</span>';

    var backTop = document.createElement("div");
    backTop.id = "mg-back-to-top";
    backTop.setAttribute("title", isEn ? "Back to top" : "Back to top");
    backTop.innerHTML = 
      '<svg viewBox="0 0 24 24" class="mg-btt-icon"><path d="M7.41 15.41L12 10.83l4.59 4.58L18 14l-6-6-6 6z"/></svg>' +
      '<span class="mg-btt-text">' + (isEn ? "TOP" : "TOP") + '</span>';

    backTop.addEventListener("click", function() {
      window.scrollTo({ top: 0, behavior: "smooth" });
    });

    window.addEventListener("scroll", function() {
      var st = window.pageYOffset || document.documentElement.scrollTop;
      if (st > 200) {
        backTop.classList.add("mg-show");
      } else {
        backTop.classList.remove("mg-show");
      }
    });

    var chatWindow = document.createElement("div");
    chatWindow.id = "mg-ai-chat-window";
    chatWindow.innerHTML = 
      '<div class="mg-ai-header">' +
        '<div class="mg-ai-header-info">' +
          '<div class="mg-ai-avatar" style="background:#ffffff; color:#059669; font-weight:700; font-size:14px; display:flex; align-items:center; justify-content:center; border:2px solid #a7f3d0; box-shadow:0 2px 6px rgba(0,0,0,0.12);">' +
            (isEn ? 'AI' : '') +
          '</div>' +
          '<div class="mg-ai-title-wrap">' +
            '<h4 id="mg-widget-title">' + aiConfig.service_name + '</h4>' +
            '<div class="mg-ai-sub"><span class="mg-ai-status-dot"></span> ' + (isEn ? 'Mellgen Official AI Assistant · Online' : 'AI · ') + '</div>' +
          '</div>' +
        '</div>' +
        '<div class="mg-ai-header-actions">' +
          '<button class="mg-ai-header-btn" id="mg-btn-clear" title="' + (isEn ? 'Clear history' : '') + '">' +
            '<svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor"><path d="M16 9v10H8V9h8m-1.5-6h-5l-1 1H5v2h14V4h-3.5l-1-1z"/></svg>' +
          '</button>' +
          '<button class="mg-ai-header-btn" id="mg-btn-close" title="' + (isEn ? 'Minimize' : '') + '">&times;</button>' +
        '</div>' +
      '</div>' +
      '<div class="mg-ai-notice-bar">' +
        '<span>' + (isEn ? '💡 Inquire specs, COA, MOQ and sample test' : '💡 、COA') + '</span>' +
        '<button class="mg-ai-switch-human-btn" id="mg-btn-to-human">' + (isEn ? 'Contact Sales' : '') + '</button>' +
      '</div>' +
      '<div class="mg-ai-body" id="mg-ai-messages"></div>' +
      '<div class="mg-ai-footer">' +
        '<div class="mg-ai-input-box">' +
          '<input type="text" class="mg-ai-input" id="mg-chat-input" placeholder="' + (isEn ? 'Ask about ingredients, specs, or COA...' : '、COA，...') + '" autocomplete="off" />' +
          '<button class="mg-ai-send-btn" id="mg-btn-send" title="' + (isEn ? 'Send' : '') + '">' +
            '<svg viewBox="0 0 24 24"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>' +
          '</button>' +
        '</div>' +
        '<div class="mg-ai-bottom-note">' + (isEn ? 'Mellgen Biotech · Official AI Support' : ' · AI') + '</div>' +
      '</div>';

    var qrModal = document.createElement("div");
    qrModal.id = "mg-ai-qr-modal";
    qrModal.innerHTML = '<img id="mg-qr-modal-img" src="" alt="Enterprise WeChat QR Code" />';

    document.body.appendChild(trigger);
    document.body.appendChild(hint);
    document.body.appendChild(backTop);
    document.body.appendChild(chatWindow);
    document.body.appendChild(qrModal);

    bindEvents();
    renderWelcome();
    fetchRemoteConfig();
  }

  function fetchRemoteConfig() {
    var xhr = new XMLHttpRequest();
    var sep = CONFIG_ENDPOINT.indexOf("?") === -1 ? "?" : "&";
    var url = CONFIG_ENDPOINT + sep + "_t=" + new Date().getTime();
    xhr.open("GET", url, true);
    xhr.onload = function() {
      if (xhr.status === 200) {
        try {
          var res = JSON.parse(xhr.responseText);
          var cfg = (res && (res.config || res.data)) ? (res.config || res.data) : null;
          if (cfg) {
            if (cfg.service_name) {
              aiConfig.service_name = cfg.service_name;
              var titleEl = document.getElementById("mg-widget-title");
              if (titleEl) titleEl.innerText = cfg.service_name;
            }
            if (cfg.welcome_message) aiConfig.welcome_message = cfg.welcome_message;
            if (cfg.default_phones) aiConfig.default_phones = cfg.default_phones;
            if (cfg.fallback_phone) aiConfig.fallback_phone = cfg.fallback_phone;
            if (cfg.wechat_qrcode_url) aiConfig.wechat_qrcode_url = cfg.wechat_qrcode_url;
            if (cfg.fallback_wechat_qrcode) aiConfig.fallback_wechat_qrcode = cfg.fallback_wechat_qrcode;
            if (cfg.preset_questions && cfg.preset_questions.length > 0) {
              aiConfig.preset_questions = cfg.preset_questions;
            }
            if (chatHistory.length === 0) {
              var msgContainer = document.getElementById("mg-ai-messages");
              if (msgContainer) {
                msgContainer.innerHTML = "";
                renderWelcome();
              }
            }
          }
        } catch(e) {}
      }
    };
    xhr.send();
  }

  function hookSidebarContact() {
    var sidebar = document.getElementById("client-2112");
    if (!sidebar) return;

    var existingItem = sidebar.querySelector(".my-kefu-link");
    if (!existingItem) {
      var aiLi = document.createElement("li");
      aiLi.className = "my-kefu-ai-chat";
      aiLi.style.cssText = "cursor: pointer; background: #059669; color: #fff; text-align: center; padding: 6px 0; border-radius: 4px; margin-bottom: 4px;";
      aiLi.innerHTML = '<p style="margin:0; font-size:12px; font-weight:600; line-height:1.2;">🤖<br>' + (isEn ? 'AI<br>Support' : 'AI') + '</p>';
      aiLi.addEventListener("click", function(e) {
        e.preventDefault();
        openChat();
      });
      sidebar.insertBefore(aiLi, sidebar.firstChild);
    } else {
      existingItem.style.display = "block";
      existingItem.addEventListener("click", function(e) {
        e.preventDefault();
        openChat();
      });
    }
  }

  function bindEvents() {
    var trigger = document.getElementById("mg-ai-trigger");
    var hint = document.getElementById("mg-ai-bubble-hint");
    var btnClose = document.getElementById("mg-btn-close");
    var btnClear = document.getElementById("mg-btn-clear");
    var btnSend = document.getElementById("mg-btn-send");
    var input = document.getElementById("mg-chat-input");
    var btnToHuman = document.getElementById("mg-btn-to-human");
    var qrModal = document.getElementById("mg-ai-qr-modal");

    trigger.addEventListener("click", function() {
      toggleChat();
    });

    hint.addEventListener("click", function(e) {
      if (e.target.classList.contains("mg-hint-close")) {
        hint.style.display = "none";
        e.stopPropagation();
      } else {
        openChat();
        hint.style.display = "none";
      }
    });

    btnClose.addEventListener("click", function() {
      closeChat();
    });

    btnClear.addEventListener("click", function() {
      if (confirm(isEn ? "Are you sure you want to clear chat history?" : "Are you sure you want to clear chat history?")) {
        chatHistory = [];
        var msgContainer = document.getElementById("mg-ai-messages");
        msgContainer.innerHTML = "";
        renderWelcome();
      }
    });

    btnSend.addEventListener("click", function() {
      sendMessage();
    });

    input.addEventListener("keydown", function(e) {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
      }
    });

    btnToHuman.addEventListener("click", function() {
      sendQuestion(isEn ? "Connect with Account Manager" : "Connect with Account Manager");
    });

    qrModal.addEventListener("click", function() {
      qrModal.classList.remove("mg-show");
    });
  }

  function toggleChat() {
    if (isOpen) {
      closeChat();
    } else {
      openChat();
    }
  }

  function openChat() {
    var win = document.getElementById("mg-ai-chat-window");
    var hint = document.getElementById("mg-ai-bubble-hint");
    win.classList.add("mg-show");
    if (hint) hint.style.display = "none";
    isOpen = true;
    setTimeout(function() {
      var input = document.getElementById("mg-chat-input");
      if (input) input.focus();
    }, 150);
  }

  function closeChat() {
    var win = document.getElementById("mg-ai-chat-window");
    win.classList.remove("mg-show");
    isOpen = false;
  }

  function renderWelcome() {
    var msgContainer = document.getElementById("mg-ai-messages");
    if (!msgContainer) return;

    var welcomeRow = document.createElement("div");
    welcomeRow.className = "mg-msg-row mg-bot";

    var suggestionsHtml = "";
    if (aiConfig.preset_questions && aiConfig.preset_questions.length > 0) {
      suggestionsHtml = '<div class="mg-qa-suggestions">';
      for (var i = 0; i < aiConfig.preset_questions.length; i++) {
        var q = aiConfig.preset_questions[i];
        suggestionsHtml += '<div class="mg-qa-chip" data-question="' + escapeHtml(q) + '">' + escapeHtml(q) + '</div>';
      }
      suggestionsHtml += '</div>';
    }

    welcomeRow.innerHTML = 
      '' + '<div class="mg-msg-mini-avatar">' + (isEn ? "AI" : "AI") + '</div>' + '' +
      '<div>' +
        '<div class="mg-msg-content">' + escapeHtml(aiConfig.welcome_message) + '</div>' +
        suggestionsHtml +
      '</div>';

    msgContainer.appendChild(welcomeRow);

    var chips = welcomeRow.querySelectorAll(".mg-qa-chip");
    chips.forEach(function(chip) {
      chip.addEventListener("click", function() {
        var q = this.getAttribute("data-question");
        sendQuestion(q);
      });
    });

    scrollToBottom();
  }

  function sendMessage() {
    var input = document.getElementById("mg-chat-input");
    var text = input.value.trim();
    if (!text || isWaiting) return;
    input.value = "";
    sendQuestion(text);
  }

  function sendQuestion(questionText) {
    if (!questionText || isWaiting) return;
    isWaiting = true;

    appendUserMessage(questionText);

    var typingIndicator = showTypingIndicator();

    var payload = {
      message: questionText,
      history: chatHistory,
      session_id: sessionId,
      question_count: userQuestionCount
    };

    var xhr = new XMLHttpRequest();
    xhr.open("POST", CHAT_ENDPOINT, true);
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");

    xhr.onload = function() {
      removeTypingIndicator(typingIndicator);
      isWaiting = false;

      if (xhr.status === 200) {
        try {
          var res = JSON.parse(xhr.responseText);
          if (res.code === 0 && res.data) {
            handleBotResponse(res.data);
          } else {
            handleFallbackResponse(isEn ? "The service is currently busy. Please try again or contact our account manager." : "，。");
          }
        } catch(e) {
          handleFallbackResponse(isEn ? "Sorry, data processing issue. Here is our account manager contact info." : "，，。");
        }
      } else {
        handleFallbackResponse(isEn ? "Network fluctuation detected. Please contact our hotline for immediate assistance." : "，。");
      }
    };

    xhr.onerror = function() {
      removeTypingIndicator(typingIndicator);
      isWaiting = false;
      handleFallbackResponse(isEn ? "Network error. Please call our account manager directly." : "，。。");
    };

    xhr.send(JSON.stringify(payload));
  }

  function handleBotResponse(data) {
    var answer = data.answer || "";
    var contactCard = data.contact_card || null;
    var needsHuman = !!data.needs_human;

    if (userQuestionCount >= 10 || data.suggest_manager) {
      needsHuman = true;
      if (!contactCard) {
        contactCard = {
          title: "Mellgen Dedicated Account Manager",
          phones: aiConfig.default_phones,
          wechat_qrcode: aiConfig.wechat_qrcode_url,
          wechat_hint: isEn ? "Scan to connect with your dedicated account manager for custom formulation and tiered pricing" : "，"
        };
      } else {
        contactCard.title = isEn ? "Mellgen Dedicated Account Manager" : "Mellgen Dedicated Account Manager";
      }
    }

    chatHistory.push({ role: "assistant", content: answer });

    appendBotMessage(answer, contactCard, needsHuman);
  }

  function handleFallbackResponse(errorText) {
    var fallbackCard = {
      title: isEn ? "Mellgen Dedicated Account Manager" : "Mellgen Dedicated Account Manager Support",
      reason: errorText,
      phones: aiConfig.default_phones,
      wechat_qrcode: aiConfig.wechat_qrcode_url,
      wechat_hint: isEn ? "Scan to connect with your dedicated account manager for fast samples and quotes" : "，"
    };
    appendBotMessage(errorText, fallbackCard, true);
  }

  function appendUserMessage(text) {
    userQuestionCount++;
    var msgContainer = document.getElementById("mg-ai-messages");
    var row = document.createElement("div");
    row.className = "mg-msg-row mg-user";
    row.innerHTML = 
      '<div class="mg-msg-content">' + escapeHtml(text) + '</div>';
    msgContainer.appendChild(row);
    chatHistory.push({ role: "user", content: text });
    scrollToBottom();
  }

  function appendBotMessage(text, contactCard, needsHuman) {
    var msgContainer = document.getElementById("mg-ai-messages");
    var row = document.createElement("div");
    row.className = "mg-msg-row mg-bot";

    var cardHtml = "";
    if (contactCard) {
      var phoneListHtml = "";
      if (contactCard.phones && contactCard.phones.length > 0) {
        phoneListHtml = '<div class="mg-human-phones">';
        contactCard.phones.forEach(function(ph) {
          phoneListHtml += 
            '<a class="mg-phone-btn" href="tel:' + ph.replace(/[^0-9]/g, "") + '">' +
              '<span>📞 ' + escapeHtml(ph) + '</span>' +
            '</a>';
        });
        phoneListHtml += '</div>';
      }

      var qrHtml = "";
      var qrUrl = contactCard.wechat_qrcode || aiConfig.wechat_qrcode_url;
      if (qrUrl) {
        qrHtml = 
          '<div class="mg-qrcode-wrap">' +
            '<img class="mg-qrcode-img" src="' + escapeHtml(qrUrl) + '" alt="Mellgen WeChat Support" title="" />' +
            '<div class="mg-qrcode-hint">' + escapeHtml(contactCard.wechat_hint || (isEn ? "Scan WeChat QR code to connect" : "")) + '</div>' +
          '</div>';
      }

      var cardClass = needsHuman ? "mg-human-card" : "mg-human-card primary-mode";
      cardHtml = 
        '<div class="' + cardClass + '">' +
          '<div class="mg-human-title">👨‍💼 ' + escapeHtml(contactCard.title || (isEn ? "Account Manager Channel" : "")) + '</div>' +
          '<div style="font-size:12px; color:#475569; margin-bottom:4px;">' + escapeHtml(contactCard.reason || "") + '</div>' +
          phoneListHtml +
          qrHtml +
        '</div>';
    }

    var formattedText = escapeHtml(text).replace(/\n/g, "<br>");

    row.innerHTML = 
      '' + '<div class="mg-msg-mini-avatar">' + (isEn ? "AI" : "AI") + '</div>' + '' +
      '<div style="max-width: 100%;">' +
        '<div class="mg-msg-content">' + formattedText + '</div>' +
        cardHtml +
      '</div>';

    msgContainer.appendChild(row);

    var qrImgs = row.querySelectorAll(".mg-qrcode-img");
    qrImgs.forEach(function(img) {
      img.addEventListener("click", function() {
        var modal = document.getElementById("mg-ai-qr-modal");
        var modalImg = document.getElementById("mg-qr-modal-img");
        modalImg.src = this.src;
        modal.classList.add("mg-show");
      });
    });

    scrollToBottom();
  }

  function showTypingIndicator() {
    var msgContainer = document.getElementById("mg-ai-messages");
    var row = document.createElement("div");
    row.className = "mg-msg-row mg-bot";
    row.id = "mg-temp-typing";
    row.innerHTML = 
      '' + '<div class="mg-msg-mini-avatar">' + (isEn ? "AI" : "AI") + '</div>' + '' +
      '<div class="mg-typing-indicator">' +
        '<span class="mg-typing-dot"></span>' +
        '<span class="mg-typing-dot"></span>' +
        '<span class="mg-typing-dot"></span>' +
      '</div>';
    msgContainer.appendChild(row);
    scrollToBottom();
    return row;
  }

  function removeTypingIndicator(el) {
    if (el && el.parentNode) {
      el.parentNode.removeChild(el);
    }
  }

  function scrollToBottom() {
    var msgContainer = document.getElementById("mg-ai-messages");
    if (msgContainer) {
      setTimeout(function() {
        msgContainer.scrollTop = msgContainer.scrollHeight;
      }, 50);
    }
  }

  function escapeHtml(str) {
    if (!str) return "";
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  function getAssetPrefix() {
    var scripts = document.getElementsByTagName("script");
    for (var i = 0; i < scripts.length; i++) {
      var src = scripts[i].getAttribute("src") || "";
      if (src.indexOf("ai_chat_widget.js") !== -1) {
        var idx = src.indexOf("js/ai_chat_widget.js");
        if (idx !== -1) {
          return src.substring(0, idx);
        }
      }
    }
    // Fallback: check path depth
    var clean = (window.location.pathname || "").replace(/^\/+/, "");
    var parts = clean.split("/").filter(function(p){ return p.length > 0; });
    if (parts.length > 1) {
      var depth = parts.length - 1;
      var p = "";
      for (var d = 0; d < depth; d++) p += "../";
      return p;
    }
    return "./";
  }

  function loadCss(url) {
    if (document.getElementById("mg-ai-chat-css")) return;
    var link = document.createElement("link");
    link.id = "mg-ai-chat-css";
    link.rel = "stylesheet";
    link.type = "text/css";
    link.href = url;
    document.head.appendChild(link);
  }

  function init() {
    removeOldSidebar();
    setTimeout(removeOldSidebar, 200);
    setTimeout(removeOldSidebar, 800);
    setTimeout(removeOldSidebar, 2000);

    try {
      if (window.MutationObserver) {
        var obs = new MutationObserver(function() {
          removeOldSidebar();
        });
        obs.observe(document.documentElement, { childList: true, subtree: true });
      }
    } catch(e) {}

    var prefix = getAssetPrefix();
    loadCss(prefix + "css/ai_chat_widget.css?v=20260912v12");

    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", createWidgetDOM);
    } else {
      createWidgetDOM();
    }
  }

  init();

  window.MellgenAIChat = {
    open: openChat,
    close: closeChat,
    ask: sendQuestion
  };

})();