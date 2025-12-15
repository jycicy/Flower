// static/js/message.js
(function (window) {
  // 消息组件类
  class Message {
    constructor() {
      this.init();
    }

    // 初始化消息组件
    init() {
      // 创建消息容器
      this.messageContainer = document.createElement('div');
      this.messageContainer.className = 'message-container';
      this.messageContainer.id = 'messageContainer';
      this.messageContainer.innerHTML = `
        <div class="message-box" id="messageBox">
          <i class="fas fa-check-circle"></i>
          <span class="message-text" id="messageText"></span>
        </div>
      `;

      // 添加样式
      this.addStyles();

      // 将消息容器添加到页面
      document.body.appendChild(this.messageContainer);
    }

    // 添加样式
    addStyles() {
      // 检查是否已添加过样式
      if (document.getElementById('message-styles')) {
        return;
      }

      const style = document.createElement('style');
      style.id = 'message-styles';
      style.textContent = `
        .message-container {
          position: fixed;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          z-index: 9999;
          display: flex;
          justify-content: center;
          align-items: center;
          pointer-events: none;
        }

        .message-box {
          background: rgba(255, 255, 255, 0.95);
          backdrop-filter: blur(10px);
          border-radius: 10px;
          padding: 20px 30px;
          box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
          text-align: center;
          min-width: 250px;
          border-left: 5px solid #ff6b6b;
          opacity: 0;
          transform: translateY(20px);
          transition: all 0.3s ease-out;
          pointer-events: auto;
        }

        .message-box.show {
          opacity: 1;
          transform: translateY(0);
        }

        .message-box.hide {
          opacity: 0;
          transform: translateY(-20px);
        }

        .message-box.success {
          border-left-color: #20bf6b;
        }

        .message-box.error {
          border-left-color: #ff6b6b;
        }

        .message-box.warning {
          border-left-color: #f39c12;
        }

        .message-box i {
          font-size: 24px;
          margin-right: 10px;
          vertical-align: middle;
        }

        .message-box.success i {
          color: #20bf6b;
        }

        .message-box.error i {
          color: #ff6b6b;
        }

        .message-box.warning i {
          color: #f39c12;
        }

        .message-text {
          font-size: 16px;
          font-weight: 500;
          color: #1a1a2e;
          display: inline-block;
          vertical-align: middle;
        }

        @media (max-width: 768px) {
          .message-box {
            min-width: 200px;
            padding: 15px 20px;
            margin: 0 20px;
          }
        }
      `;

      document.head.appendChild(style);
    }

    // 显示消息
    show(message, type = 'success') {
      const messageBox = this.messageContainer.querySelector('#messageBox');
      const messageText = this.messageContainer.querySelector('#messageText');
      const icon = messageBox.querySelector('i');

      // 设置消息内容
      messageText.textContent = message;

      // 设置消息类型样式
      messageBox.className = 'message-box ' + type;

      // 设置图标
      if (type === 'success') {
        icon.className = 'fas fa-check-circle';
      } else if (type === 'error') {
        icon.className = 'fas fa-exclamation-circle';
      } else if (type === 'warning') {
        icon.className = 'fas fa-exclamation-triangle';
      } else {
        icon.className = 'fas fa-info-circle';
      }

      // 显示消息框
      this.messageContainer.style.display = 'flex';

      // 触发重排后添加show类实现动画
      setTimeout(() => {
        messageBox.classList.add('show');
      }, 10);

      // 3秒后自动隐藏
      setTimeout(() => {
        messageBox.classList.remove('show');
        messageBox.classList.add('hide');

        // 动画结束后隐藏容器
        setTimeout(() => {
          this.messageContainer.style.display = 'none';
          messageBox.classList.remove('hide');
        }, 300);
      }, 2000);
    }

    // 显示成功消息
    success(message) {
      this.show(message, 'success');
    }

    // 显示错误消息
    error(message) {
      this.show(message, 'error');
    }

    // 显示警告消息
    warning(message) {
      this.show(message, 'warning');
    }
  }

  // 创建全局实例
  window.Message = new Message();

})(window);


