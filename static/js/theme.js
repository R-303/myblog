( function () {
    const root=document.documentElement;
    const button=document.getElementByID("theme-toggle");

    if(!button) {
        return;
    }

    function currentTheme() {
        return root.dataset.theme==="dark" ? "dark" : "light";
    }

    function updateButton(theme) {
        if(theme==="dark") {
            button.textContent="☀️";
            button.setAttribute("arial-label","切换到白天模式");
            button.setAttribute("title","切换到白天模式");
        } else {
            button.textContent="🌙";
            button.setAttribute("arial-label","切换到黑夜模式");
            button.setAttribute("title","切换到黑夜模式");
        }
    }

    updateButton(currentTheme());

    button.addEventListener("click",function () {
        const nextTheme=
            currentTheme()==="dark" ? "light" : "dark";

        if(nextTheme==="dark") {
            root.dataset.theme="dark";
        } else {
            delete root.dataset.theme;
        }

        try {
            localStorage.setItem("myblog-theme",nextTheme);
        } catch (error) {
            // 浏览器禁用 localStorage 时，仍然允许当前页面切换
        }

        updateButton(nextTheme);
    });
})();