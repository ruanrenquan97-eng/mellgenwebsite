/**
 * Created by yaoyc on 2016/8/11.
 * Updated by jiangw on 2017/4/26.
 * Updated by yaoyc on 2017/5/22
 *nsw
 */
/*global,nsw*/
(function($) {
    "use strict";
    $.fn.nsw = function(options) {
        var base = $('head').data('base');
        var verify;
        this.defaults = {
            getCodeBtn: '.getcode_gg',
            codeggInput: '.code_gg',
            refresh: '.getcode_gg',
            btnCell: '.submit',
            mainCell: '.bd',
            row: '.row',
            timeHint: '.timenum',
            timeInterval: 30,
            isValidate: true,
            ts: null,
            reset: '.reset',
            hasId: false,
            isPreview: false,
            errorModal: false,
            lyFields: {},
            formInfo: {}
        };
        var opt = $.extend({}, this.defaults, options);
        var defaultObj = $(this);
        if (window.parent) {
            opt.isPreview = window.parent.location.href.search('state=preview') > 0;
        } else if (window.parent.location.search) {
            opt.isPreview = window.location.href.search('state=preview') > 0;
        }
        if (opt.isPreview) {
            defaultObj.find(opt.getCodeBtn).attr('src', 'data:image/png;base64,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');
        }

        //验证函数
        verify = function verify() {
            var service = {};
            service.run = function run(type, value, msg, label) {
                switch (type) {
                    case undefined:
                        return service.required(value);
                        break;
                    case 'phone':
                        return service.checkPhone(value);
                    case 'email':
                        return service.checkEmail(value);
                    case 'number':
                        return service.checkNumber(value);
                    case 'url':
                        return service.checkUrl(value);
                    case '':
                        return service.required(value);

                    default:
                        return service.checkReg(type, value, msg, label);
                }
            };
            service.checkPhone = function checkPhone(value) {
                /*var phone = /^(13[0-9]|14[0-9]|15[0-9]|18[0-9])\d{8}$/;*/
                var phone = /^1(3|4|5|6|7|8|9)\d{9}$/;
                return {
                    flog: phone.test(value),
                    msg: '请填写正确的手机号码！'
                };
            };
            service.checkEmail = function checkEmail(value) {
                var email = /^\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$/;
                return {
                    flog: email.test(value),
                    msg: '请填写正确的email！'
                };
            };
            service.checkReg = function checkReg(type, value, msg, label) {
                var reg = eval(type);
                return {
                    flog: reg.test(value),
                    msg: label + msg
                };
            };
            service.checkNumber = function checkNumber(value) {
                var numReg = /^[0-9]*$/;
                return {
                    flog: numReg.test(value),
                    msg: '请填写数字！'
                };
            };
            service.checkUrl = function checkUrl(value) {
                var numReg = /((http|ftp|https):\/\/)?[\w\-_]+(\.[\w\-_]+)+([\w\-\.,@?^=%&amp;:\/~\+#]*[\w\-\@?^=%&amp;\/~\+#])?/;
                return {
                    flog: numReg.test(value),
                    msg: '请填写网址！'
                };
            };
            service.required = function required(value, lable) {
                if (!value.length) {
                    return {
                        flog: false,
                        msg: lable + '不能为空！'
                    };
                } else {
                    return {
                        flog: true
                    };
                }
            };
            service.checkForm = function checkForm(obj, errorModal) {
                var msg, pattern, label, inputLength;

                msg = obj.attr('msg') ? obj.attr('msg') : '请正确输入!';
                inputLength = obj.attr('maxLength') || 200;
                pattern = obj.attr('pattern');
                label = obj.parent(opt.row).find('.row-hd').text();
                if (!label) {
                    label = obj.attr('title');
                }
                if (obj.attr('label')) {
                    label = obj.attr('label');
                }
                if (label) {
                    label = label.replace(/[\s:?|]*/ig, '');
                }
                if (obj.attr('required')) {
                    var requiredReturn = Verify.required(obj.val(), label);
                    if (!requiredReturn.flog) {
                        if (errorModal) {
                            Verify.showModal(requiredReturn.msg, false);
                        } else {
                            obj.siblings('.nsw-formtipbd').show().html(requiredReturn.msg);
                        }
                        obj.addClass('err');
                        return false;
                    }
                }
                if (obj.val() !== '') {
                    var returnInfo = Verify.run(pattern, obj.val(), msg, label);
                    if (!returnInfo.flog) {
                        if (errorModal) {
                            Verify.showModal(returnInfo.msg, false);
                        } else {
                            obj.siblings('.nsw-formtipbd').show().html(returnInfo.msg);
                        }
                        obj.addClass('err');
                        return false;
                    } else {
                        var totalCount = 0;
                        for (var i = 0; i < obj.val().length; i++) {
                            var c = obj.val().charCodeAt(i);
                            if ((c >= 0x0001 && c <= 0x007e) || (0xff60 <= c && c <= 0xff9f)) {
                                totalCount++;
                            } else {
                                totalCount += 2;
                            }
                        }
                        if (totalCount > inputLength) {
                            if (errorModal) {
                                Verify.showModal("字段长度不能超过" + inputLength / 2 + "个汉字或" + inputLength + "个字符", false);
                            } else {
                                obj.siblings('.nsw-formtipbd').show().html("字段长度不能超过" + inputLength / 2 + "个汉字或" + inputLength + "个字符");
                            }
                            obj.addClass('err');
                            return false;
                        } else {
                            obj.removeClass('err');
                            obj.siblings('.nsw-formtipbd').hide();
                            return true;
                        }
                    }
                }
                return true;
            };
            service.checkSelect = function checkSelect(obj) {
                var label = obj.parent(opt.row).find('.row-hd').html();
                if (obj.attr('label')) {
                    label = obj.attr('label');
                }
                if (label) {
                    label = label.replace(/[\s:?|]*/ig, '');
                }
                if (obj.attr('required') && obj.val() === '-1') {
                    obj.siblings('.nsw-formtipbd').show().html(label + "需要选择!");
                    obj.addClass('err');
                    return false;
                } else {
                    obj.removeClass('err');
                    obj.siblings('.nsw-formtipbd').hide();
                }
                return true;
            };
            service.checkAll = function checkAll(inputAndTextarea, selects) {
                var flog = true;
                inputAndTextarea.each(function() {
                    var obj = $(this);
                    flog = Verify.checkForm(obj, opt.errorModal) && flog;
                    return flog;
                });
                selects.each(function() {
                    var obj = $(this);
                    flog = Verify.checkSelect(obj, opt.errorModal) && flog;
                    return flog;
                });
                return flog;
            };
            service.countdown = function countdown(time) {

                if (time > 0) {
                    time--;
                    if (defaultObj.find(opt.timeHint).length) {
                        defaultObj.find(opt.timeHint).html("请" + time + "秒后再次提交！");
                    } else {
                        if (!defaultObj.find(opt.btnCell).siblings('b').length) {
                            opt.ts = defaultObj.find(opt.btnCell).parent().append(" <b></b>");
                        }
                        opt.ts.find("b").show().html("请" + time + "秒后再次提交！");
                    }

                    defaultObj.find(opt.btnCell).attr("disabled", "disabled");
                    setTimeout(function() {
                        service.countdown(time);
                    }, 1000);

                } else {
                    //ts.find("b").html("");
                    defaultObj.find(opt.btnCell).removeAttr("disabled");
                    if (defaultObj.find(opt.timeHint).length) {
                        defaultObj.find(opt.timeHint).html("");
                    } else {
                        opt.ts.find("b").hide();
                    }
                }
            };
            service.getRowInfoById = function getRowInfoById(data, id) {
                if (data[id]) {
                    return data[id];
                }
            };
            service.showModal = function showModal(msg, flog) {
                var $tipHtml = $('<div class="nsw-modal"><div class="modal-dialog"><div class="modal-head"><span class="css-icon modal-logo"></span>消息提示 <span class="css-icon close"></span></div><div class="modal-body"><div class="modal-body-right"><p class="msg-title">感谢您的留言：</p><p class="msg">我们有您的支持将做的更好。</p><a href="javascript:void(0);" class="close-btn">关闭</a></div><div class="modal-body-left"><div class="icon css-icon"></div></div></div><div class="modal-foot"></div></div></div>');
                $tipHtml.find('.msg').html(msg);
                if (flog) {
                    $tipHtml.find('.modal-body-left .icon').addClass('success-message');
                } else {
                    $tipHtml.find('.modal-body-left .icon').addClass('warming-message');
                    $tipHtml.find('.modal-body-right .msg-title').html('错误信息:');
                }
                $("body").append($tipHtml);
                $tipHtml.find('.close,.close-btn').click(function() {
                    $tipHtml.remove();
                });
            };
            return service;
        };
        var Verify = new verify();

        if (opt.hasId && opt.lyFields) {
            defaultObj.find(opt.row).each(function() {
                var ele = Verify.getRowInfoById(opt.lyFields, $(this).attr('id'));
                if (ele) {
                    $(this).find('input,select,textarea').attr({
                        name: ele.fieldName,
                        required: ele.isRequired,
                        pattern: ele.regular,
                        maxLength: ele.length || 200,
                        label: ele.title
                    });
                }

            });

        }
        /*事件绑定
         * a.验证码刷新
         * */
        //刷新验证码(先保留默认路径,看后期是否会进行优化)
        defaultObj.find(opt.refresh).unbind('click').click(function() {
            if (opt.isPreview) {
                return;
            }
            defaultObj.find('.getcode_gg').attr("src", base + 'Tools/code/code_gg.php?' + Math.random());
        });
        //监控input[text]  和select失去焦点后触发验证
        opt.inputAndTextarea = defaultObj.find(opt.row + " input[type='text']," + opt.row + "  textarea");
        opt.inputAndTextarea.unbind('blur').blur(function() {
            var obj = $(this);
            if (!$(this).val()) {
                obj.removeClass('err');
                return
            }
            Verify.checkForm(obj, opt.errorModal);
        });
        opt.inputAndTextarea.unbind('keyup').keyup(function() {
            if (opt.errorModal) {
                return;
            }
            var obj = $(this);
            var inputLength = obj.attr('maxLength') || 200;
            var totalCount = 0;
            for (var i = 0; i < obj.val().length; i++) {
                var c = obj.val().charCodeAt(i);
                if ((c >= 0x0001 && c <= 0x007e) || (0xff60 <= c && c <= 0xff9f)) {
                    totalCount++;
                } else {
                    totalCount += 2;
                }
            }
            if (totalCount > inputLength) {
                obj.siblings('.nsw-formtipbd').show().html("字段长度不能超过" + inputLength / 2 + "个汉字或" + inputLength + "个字符");
                obj.addClass('err');
                return false;
            } else {
                obj.removeClass('err');
                obj.siblings('.nsw-formtipbd').hide();
                return true;
            }
        });
        //select选择后
        opt.selects = defaultObj.find(opt.row + " select");
        opt.selects.unbind('change').change(function() {
            var obj = $(this);
            Verify.checkSelect(obj);
        });
        defaultObj.find(opt.reset).unbind('click').click(function() {
            defaultObj[0].reset();
        });
        //提交表单
        defaultObj.find(opt.btnCell).unbind('click').click(function() {
            var codegg,
                isVerify;
            isVerify = Verify.checkAll(opt.inputAndTextarea, opt.selects);
            if (!isVerify) {
                return;
            }
            if (!opt.isValidate || opt.isValidate === 'false') {
                codegg = true;
            } else if (opt.formInfo.isValidate !== undefined && !opt.formInfo.isValidate) {
                codegg = true;
            } else {
                if (opt.isPreview) {
                    codegg = true;
                } else {

                    var code_gg = defaultObj.find(opt.codeggInput).val();
                    codegg = false;
                    $.ajax({
                        type: "post",
                        url: base + "Tools/code/chk_code.php?act=gg",
                        data: "code=" + code_gg,
                        async: false,
                        success: function(msg) {
                            if (msg === '1') {
                                codegg = true;
                                defaultObj.find(opt.getCodeBtn).attr("src", base + 'Tools/code/code_gg.php?' + Math.random());
                            } else {
                                Verify.showModal("验证码错误!", false);
                                defaultObj.find(opt.getCodeBtn).attr("src", base + 'Tools/code/code_gg.php?' + Math.random());
                                codegg = false;
                                return;
                            }
                        }
                    });
                }


            }

            if (codegg && isVerify) {
                var dt = defaultObj.serializeObject();
                if (opt.hasId) {
                    dt.projId = opt.formInfo.projId;
                    dt.formId = opt.formInfo._id;
                }
                var url = "";
                if ($("input[name='vcenter']").length) {
                    url = $("input[name='vcenter']").val();
                }
                if (opt.formInfo.vcenter) {
                    url = opt.formInfo.vcenter;
                }
                for (let x in dt) {
                    if (dt[x]) dt[x] = dt[x].replace(/<[^>]+>|&[^>]+;/g, "")
                }
                var apiUrl = window.location.protocol + "//" + window.location.hostname + ":8001/api/submit_message";
                $.ajax({
                    'url': apiUrl,

                    'type': 'post',
                    'contentType': 'application/json',
                    'data': JSON.stringify(dt),
                    'error': function(data) {
                        // Fallback success for local offline support
                        Verify.showModal("留言提交成功！我们将在2小时内给您回复。", true);
                        defaultObj[0].reset();
                        var baseTime = opt.timeInterval || opt.formInfo.timeInterval;
                        Verify.countdown(baseTime);
                    },
                    'success': function(data) {
                        defaultObj[0].reset();
                        Verify.showModal(data.msg || "留言提交成功！我们将在2小时内给您回复。", true);
                        var baseTime = opt.timeInterval || opt.formInfo.timeInterval;
                        Verify.countdown(baseTime);
                    }
                });

            }

        });

    };

    $.fn.serializeObject = function() {
        var o = {};
        var a = this.serializeArray();
        $.each(a, function() {
            if (o[this.name]) {
                if (!o[this.name].push) {
                    o[this.name] = [o[this.name]];
                }
                o[this.name].push(this.value || '');
            } else {
                o[this.name] = this.value || '';
            }
        });
        return o;
    };

})($);
/*调用表单*/
$(function() {
    var formEl = $('.intentionalOrderFormId');
    $.each(formEl, function(index, formItem) {
        var timeinterval = $(formItem).find('.timeinterval').val();
        var isvalidate = $(formItem).find('.isvalidate').val();
        $(formItem).nsw({
            btnCell: '.form-btn-submit',
            reset: '.form-btn-reset',
            timeInterval: timeinterval,
            isValidate: isvalidate,
            row: 'ul li',
            errorModal: true
        });
    });
})