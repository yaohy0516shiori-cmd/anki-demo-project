import { StrictMode } from "react"; //开发模式下帮助检查潜在问题
import { createRoot } from "react-dom/client"; //React 18/19 的挂载入口，把 React App 挂到 HTML 的 #root 节点上。
import "./index.css"; //CSS 样式文件，用于样式化 HTML 元素。
import App from "./App.tsx"; //App.tsx 是 React 应用的入口文件，包含所有页面和组件。
import { BrowserRouter } from "react-router-dom"; //React 官方提供的浏览器端路由库，用于导航到其他页面。

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>{" "}
    {/* // 使用BrowserRouter包裹App，使得App可以访问路由 */}
  </StrictMode>,
);
