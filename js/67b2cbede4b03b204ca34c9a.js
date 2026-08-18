
    $(window).scroll(function (a) {

      if ($(this).scrollTop() > 1) {
          $("#head").addClass("headFix")
      } else {
          $("#head").removeClass("headFix")
      }
  }).scroll();


        $(function(){
            var image = new Image();
            image.onload = function() {
                var imgWidth=$('.ty-banner-1 img').width();
                var imgHeight=$('.ty-banner-1 img').height();
               var length = imgWidth/2;
               if(length>0){
                    $('.ty-banner-1 img').attr({'style':'margin-left:'+ (-length) + 'px;position:absolute'});
                    $('.ty-banner-1').attr('style','height:'+ imgHeight + 'px');
               }
               $('.ty-banner-1 img').addClass('show');
            }
            image.src = $('.ty-banner-1 img').attr('src');
           
        });
    

        var key = document.getElementById("key");

        function searchInfo() {
            var base = $('head').data('base');
            if (key.value) {
                location.href = base + "search.php?key=" + key.value;
            } else {
                alert('请输入您要搜索的关键词！');
            }
        }
        key.addEventListener('keypress', function(event) {
            var keycode = event.keycode || event.which;
            if (keycode == "13") {
                searchInfo();
            }
        });

        function searchLink(el) {
            var href = $(el).attr("href");
            location.href = href ? href : "/search.php?key=" + $(el).html();
        }
    

    function resetForm() {
        $('#intentionalOrderFormId input[type=text]').val('');
        $('#intentionalOrderFormId textarea').val('');
    }
    var timeinterval = $('.timeinterval').text();
    var isvalidate = $('.isvalidate').text();
    $('#intentionalOrderFormId').nsw({
        btnCell: '.lyl-1k2-form-btn-1',
        timeInterval: timeinterval,
        row: '.findrow li',
        errorModal: true,
        isValidate: isvalidate
    });


					        var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();
					
					        function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }
					
					        function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }
					
					        function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }
					
					        var Point = function (_F3$Obj) {
					            _inherits(Point, _F3$Obj);
					
					            function Point() {
					                var radius = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : 5;
					
					                _classCallCheck(this, Point);
					
					                var _this = _possibleConstructorReturn(this, (Point.__proto__ || Object.getPrototypeOf(Point)).call(this));
					
					                _this.radius = radius;
					                _this.color = 'rgba(' + [Math.random() * 255 | 0, Math.random() * 255 | 0, Math.random() * 255 | 0, Math.random()].join(',') + ')';
					                _this.prevCrood = null;
					                return _this;
					            }
					
					            _createClass(Point, [{
					                key: 'render',
					                value: function render(ctx) {
					
					                    ctx.fillStyle = '#1061aa';
					                    ctx.fillRect(this.croods2D.position.x, this.croods2D.position.y, this.radius * this.croods2D.scale * this.yScale, this.radius * this.croods2D.scale * this.yScale);
					                }
					            }]);
					
					            return Point;
					        }(F3.Obj);
					
					        var planeFunctions = {
					            'sin(sqrt(x^2+z^2))': function sinSqrtX2Z2(x, z, offset) {
					                return Math.sin(Math.sqrt(Math.pow(x / 2, 2) + Math.pow(z / 2, 2)) - offset);
					            },
					            'cos(x)*sin(z)': function cosXSinZ(x, z, offset) {
					                return Math.cos(x / 8 + offset) * Math.sin(z / 8 + offset) * 1;
					            }
					        };
					
					        var Effect = function (_F3$Time) {
					            _inherits(Effect, _F3$Time);
					
					            function Effect(renderer, scene, camera, cvs) {
					                _classCallCheck(this, Effect);
					
					                var _this2 = _possibleConstructorReturn(this, (Effect.__proto__ || Object.getPrototypeOf(Effect)).call(this));
					
					                _this2.renderer = renderer;
					                _this2.scene = scene;
					                _this2.camera = camera;
					                _this2.cvs = cvs;
					
					                _this2.xOffset = 0;
					                _this2.waveHeight = 0.4; // 波高
					                _this2.waveWidth = 8; // 波长
					
					                _this2.col = 40;
					                _this2.colPointNum = 40;
					
					                _this2.flyTime = 2000;
					                _this2.timePass = 0;
					
					                _this2.scale = 1;
					                _this2.scaleStep = 0.01;
					
					                _this2.planeFunction = function () {
					                    return 0;
					                };
					                _this2.rotate = { x: false, y: false, z: false };
					
					                _this2.pointGroup = new F3.Obj();
					                _this2.scene.add(_this2.pointGroup);
					
					                _this2.resize(cvs.width, cvs.height);
					                _this2.init();
					                return _this2;
					            }
					
					            _createClass(Effect, [{
					                key: 'resize',
					                value: function resize(width, height) {
					                    this.cvs.width = width;
					                    this.cvs.height = height;
					                    // this.pointGroup.position.set(this.cvs.width/2, this.cvs.height, 0);
					                    this.stepWidth = width * 4 / this.col;
					                    this.pointGroup.setPosition(this.cvs.width / 4, this.cvs.height * 1.2, -this.col * this.stepWidth / 4);
					                    this.pointGroup.setRotation(0.1, 0, 0);
					                    // this.waveHeight = height/2;
					                    // this.waveWidth = this.waveHeight * 4;
					                    // console.log(this.stepWidth);
					                }
					            }, {
					                key: 'init',
					                value: function init() {
					                    // create point
					                    var point;
					                    for (var x = -(this.col - 1) / 2, count = 0; x <= (this.col - 1) / 2; x++) {
					                        for (var z = -(this.colPointNum - 1) / 2; z <= (this.colPointNum - 1) / 2; z++) {
					                            point = new Point(10);
					                            this.pointGroup.add(point);
					                            /*point.initPos = new F3.Vector3(
					                                 x + Math.random() * -2 + 1,
					                                 -30 + -10 * Math.random(),
					                                 z + Math.random() * -2 + 1
					                            );*/
					                            point.initPos = new F3.Vector3(0, 0, 0);
					                            point.flyDelay = 0; //Math.random() * 1000 | 0;
					                        }
					                    }
					                }
					            }, {
					                key: 'update',
					                value: function update(delta) {
					                    this.timePass += delta;
					                    this.xOffset = this.timePass / 500;
					
					                    var point = void 0;
					                    var flyPecent = void 0;
					                    var x = void 0,
					                        y = void 0,
					                        z = void 0;
					                    var count = 0;
					
					                    // if (this.timePass < 100)
					                    for (x = -(this.col - 1) / 2; x <= (this.col - 1) / 2; x++) {
					                        for (z = -(this.colPointNum - 1) / 2; z <= (this.colPointNum - 1) / 2; z++) {
					
					                            // let y = Math.cos(x*Math.PI/this.waveWidth + this.xOffset)*Math.sin(z*Math.PI/this.waveWidth + this.xOffset) * this.waveHeight;
					
					                            y = this.planeFunction(x, z, this.xOffset);
					                            // let y = Math.sin(Math.sqrt(Math.pow(x/v, 2)+Math.pow(z/v, 2)) - this.xOffset) * 1
					                            // console.log(y);
					
					                            point = this.pointGroup.children[count];
					                            point.yScale = 1; //(-y + 0.6)/(this.waveHeight) * 1.5;
					
					                            flyPecent = (this.timePass - point.flyDelay) / this.flyTime;
					                            flyPecent = flyPecent > 1 ? 1 : flyPecent < 0 ? 0 : flyPecent;
					
					                            point.setPosition(x * this.stepWidth, y * this.stepWidth, z * this.stepWidth);
					                            count++;
					                        }
					                    }
					                    if (this.rotate.x || this.rotate.y || this.rotate.z) {
					                        this.pointGroup.setRotation(this.rotate.x ? this.pointGroup.rotation.x + 0.001 : 0, this.rotate.y ? this.pointGroup.rotation.y + 0.001 : 0, this.rotate.z ? this.pointGroup.rotation.z + 0.001 : 0);
					                    }
					                }
					            }, {
					                key: 'setFunction',
					                value: function setFunction(fun) {
					                    this.planeFunction = fun;
					                }
					            }, {
					                key: 'toggleRotate',
					                value: function toggleRotate(r) {
					                    this.rotate[r] = !this.rotate[r];
					                    if (!this.rotate[r]) {
					                        this.pointGroup.rotation[r] = 0;
					                    }
					                }
					            }, {
					                key: 'animate',
					                value: function animate() {
					                    var _this3 = this;
					
					                    this.addTick(function (delta) {
					                        _this3.update(delta);
					                        _this3.renderer.render(_this3.scene, _this3.camera);
					                    });
					                }
					            }]);
					
					            return Effect;
					        }(F3.Time);
					
					        function init(cvs) {
					            var ctx = cvs.getContext('2d');
					
					            var scene = new F3.Scene();
					            var camera = new F3.Camera();
					            camera.origin = new F3.Vector3(cvs.width / 2, cvs.height / 5);
					            camera.p = 200;
					
					            var renderer = new F3.Renderer(ctx, cvs);
					            var effect = new Effect(renderer, scene, camera, cvs);
					            effect.animate();
					
					            var functions = document.querySelector('.functions');
					            var btnHTML = '';
					            for (var name in planeFunctions) {
					                btnHTML += '<div class="btn" data-function="' + name + '">' + name + '</div>';
					            }
					            functions.innerHTML = btnHTML;
					
					            var btns = functions.querySelectorAll('.btn');
					            function selectFunction(funName) {
					                btns.forEach(function (btn) {
					                    var dataFunction = btn.dataset.function;
					                    if (dataFunction === funName) {
					                        btn.classList.add('active');
					                        effect.setFunction(planeFunctions[funName]);
					                    } else {
					                        btn.classList.remove('active');
					                    }
					                });
					            }
					            selectFunction(btns[0].dataset.function);
					            functions.addEventListener('click', function (e) {
					                if (e.target.dataset.function) {
					                    selectFunction(e.target.dataset.function);
					                }
					            });
					
					            var rotate = document.querySelector('.rotate');
					            var rotateBtns = rotate.querySelectorAll('.btn');
					            function toggleRotate(_r) {
					                rotateBtns.forEach(function (rotateBtn) {
					                    var r = rotateBtn.dataset.rotate;
					                    if (r === _r) {
					                        rotateBtn.classList.toggle('active');
					                        effect.toggleRotate(r);
					                    }
					                });
					            }
					            toggleRotate('y');
					            rotate.addEventListener('click', function (e) {
					                if (e.target.dataset.rotate) {
					                    toggleRotate(e.target.dataset.rotate);
					                }
					            });
					
					            F3.TIME.start();
					        }
					        init(document.querySelector('canvas'));
					    

    $(function() {
        var time;
        //var winHeight = top.window.document.body.clientHeight || $(window.parent).height();
        $('.xin-2112-client-1').css({
            'marginTop': -($('.xin-2112-client-1').height() / 2)
        });
        $("#client-2112").find("li").mouseover(function() {
                $(this).addClass("cur").siblings("li").removeClass("cur")
            })
            //返回顶部
        $(window).scroll(function() {
            var scrollTop = document.documentElement.scrollTop || window.pageYOffset || document.body.scrollTop;
            var eltop = $("#client-2112").find(".my-kefu-top");
            if (scrollTop > 0) {
                eltop.show();
            } else {
                eltop.hide();
            }
        });
        $("#client-2112").find(".my-kefu-top").click(function() {
            var scrollTop = document.documentElement.scrollTop || window.pageYOffset || document.body.scrollTop;
            if (scrollTop > 0) {
                $("html,body").animate({
                    scrollTop: 0
                }, "slow");
            }
        });
    });

