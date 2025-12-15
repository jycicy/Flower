/**
 * 封装 fetch API，支持完整的 HTTP 请求功能
 * @param {string} url - 请求 URL
 * @param {Object} options - 请求配置
 * @param {string} [options.method='GET'] - 请求方法
 * @param {Object} [options.data] - 请求数据
 * @param {Object} [options.headers] - 请求头
 * @param {number} [options.timeout=30000] - 超时时间（毫秒）
 * @param {number} [options.retry=0] - 重试次数
 * @param {Function} [options.beforeRequest] - 请求前拦截函数
 * @param {Function} [options.afterResponse] - 响应后拦截函数
 * @returns {Promise<Object>} - 返回响应数据的 Promise
 */
async function http(url, options = {}) {
  const {
    method = 'GET',
    data = {},
    headers = {},
    timeout = 30000,
    retry = 0,
    beforeRequest,
    afterResponse
  } = options;

  // 请求前拦截
  let processedUrl = url;
  let processedConfig = {
    method: method.toUpperCase(),
    headers: {
      'Content-Type': 'application/json',

      ...headers
    }
  };

  if (typeof beforeRequest === 'function') {
    [processedUrl, processedConfig] = beforeRequest(processedUrl, processedConfig);
  }

  // 处理 GET 请求的查询参数
  if (processedConfig.method === 'GET' && Object.keys(data).length > 0) {
    const queryString = new URLSearchParams(data).toString();
    processedUrl += (processedUrl.includes('?') ? '&' : '?') + queryString;
  }

  // 处理 POST 请求的数据
  if (processedConfig.method === 'POST' && Object.keys(data).length > 0) {
    processedConfig.body = JSON.stringify(data);
  }

  // 添加超时处理
  const controller = new AbortController();
  const signal = controller.signal;
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  let attempt = 0;
  async function sendRequest() {
    try {
      // 发送请求
      const response = await fetch(processedUrl, { ...processedConfig, signal });

      // 清除超时计时器
      clearTimeout(timeoutId);

      // 检查 HTTP 状态码
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // 解析响应
      const result = await response.json();

      // 响应后拦截
      return typeof afterResponse === 'function'
        ? afterResponse(result)
        : result;

    } catch (error) {
      // 清除超时计时器
      clearTimeout(timeoutId);

      // 处理可重试的错误
      if (attempt < retry && (
        error.name === 'AbortError' || // 超时错误
        error.message.includes('Network') // 网络错误
      )) {
        attempt++;
        console.log(`请求失败，正在进行第 ${attempt} 次重试...`);
        return sendRequest();
      }

      // 不可重试的错误，抛出异常
      console.error('Request failed:', error);
      throw error;
    }
  }

  return sendRequest();
}

// 使用示例
// http('https://api.example.com/users', {
//   method: 'GET',
//   timeout: 10000, // 10秒超时
//   retry: 2, // 失败重试2次
//   beforeRequest: (url, config) => {
//     // 添加认证头
//     config.headers.Authorization = 'Bearer token123';
//     return [url, config];
//   },
//   afterResponse: (response) => {
//     // 统一处理响应格式
//     return response.data || response;
//   }
// });