document.addEventListener('DOMContentLoaded', () => {
  console.log('购物车脚本加载成功');

  // 确认 CSRF 令牌存在
  const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]')?.value;
  console.log('CSRF 令牌:', csrfToken ? '存在' : '未找到');

  // 使用事件委托绑定点击事件
  document.body.addEventListener('click', (event) => {
    if (event.target.classList.contains('add-to-cart')) {
      const button = event.target;
      console.log('点击事件触发，商品 ID:', button.dataset.id);

      // 更新按钮状态
      button.disabled = true;
      button.innerHTML = '<i class="fa fa-spinner fa-spin"></i> 添加中...';

      // 发送 AJAX 请求
      fetch('/add_to_cart/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({
          id: button.dataset.id,
          title: button.dataset.title,
          price: button.dataset.price
        })
      })
        .then(response => {
          if (!response.ok) throw new Error(`HTTP 错误: ${response.status}`);
          return response.json();
        })
        .then(data => {
          console.log('添加购物车结果:', data);
          alert(data.message);
        })
        .catch(error => {
          console.error('添加购物车失败:', error);
          alert('操作失败，请重试');
        })
        .finally(() => {
          // 恢复按钮状态
          button.disabled = false;
          button.innerHTML = '+ <span class="glyphicon glyphicon-shopping-cart"></span>';
        });
    }
  });
});