document.addEventListener("DOMContentLoaded", () => {
    const rankingList = document.querySelector(".ranking-list");
    if (!rankingList) return;

    function ordenarRanking() {
        const items = Array.from(rankingList.children);

        items.sort((a, b) => {
            const scoreA = parseFloat(a.querySelector("span").textContent) || 0;
            const scoreB = parseFloat(b.querySelector("span").textContent) || 0;
            return scoreB - scoreA;
        });

        items.forEach((item, index) => {
            item.classList.remove("top1","top2","top3");
            if (index === 0) item.classList.add("top1");
            if (index === 1) item.classList.add("top2");
            if (index === 2) item.classList.add("top3");
        });

        items.forEach(item => rankingList.appendChild(item));
    }

    ordenarRanking();

    const observer = new MutationObserver(() => {
        ordenarRanking();
    });

    observer.observe(rankingList, { childList: true });
});
