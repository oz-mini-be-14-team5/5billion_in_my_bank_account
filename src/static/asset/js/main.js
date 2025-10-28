const endpoints = {
    quote: "/api/v1/quotes/",
    posts: "/api/v1/posts/?limit=5"
};

const quoteTextEl = document.getElementById("quote-text");
const quoteAuthorEl = document.getElementById("quote-author");
const quoteCopyBtn = document.getElementById("quote-copy");
const noteEl = document.querySelector(".quote-card__note");
const recentListEl = document.getElementById("recent-posts");
const tabToday = document.getElementById("tab-today");
const tabDiary = document.getElementById("tab-my-diary");

async function fetchJson(url) {
    const response = await fetch(url, { headers: { Accept: "application/json" } });
    if (!response.ok) {
        const err = new Error(`Request failed: ${response.status}`);
        err.status = response.status;
        throw err;
    }
    return response.json();
}

function setQuoteText(message, author) {
    if (quoteTextEl) {
        quoteTextEl.textContent = message;
    }
    if (quoteAuthorEl) {
        quoteAuthorEl.textContent = author ? `– ${author}` : "";
    }
}

async function loadQuote() {
    try {
        const data = await fetchJson(endpoints.quote);
        if (!data) {
            setQuoteText("아직 등록된 명언이 없어요.", "");
            return;
        }
        setQuoteText(data.message, data.author);
    } catch (error) {
        console.error(error);
        setQuoteText("명언을 불러오지 못했습니다.", "");
    }
}

function formatDate(dateStr) {
    try {
        const date = new Date(dateStr);
        if (!Number.isNaN(date.getTime())) {
            const month = `${date.getMonth() + 1}`.padStart(2, "0");
            const day = `${date.getDate()}`.padStart(2, "0");
            return `${month}/${day}`;
        }
    } catch (error) {
        console.error("Invalid date", error);
    }
    return "";
}

function renderRecentPosts(posts) {
    if (!recentListEl) return;
    if (!Array.isArray(posts) || posts.length === 0) {
        recentListEl.innerHTML = `
            <li class="recent__item recent__item--empty">
                <span class="recent__date">-</span>
                <div class="recent__entry">
                    <p class="recent__text recent__text--empty">최근 작성한 일기가 없습니다.</p>
                </div>
            </li>
        `;
        return;
    }

    recentListEl.innerHTML = "";
    posts.forEach((post) => {
        const item = document.createElement("li");
        item.className = "recent__item";
        const displayDate = formatDate(post.date) || formatDate(post.created_at) || "-";
        item.innerHTML = `
            <span class="recent__date">${displayDate}</span>
            <div class="recent__entry">
                <img class="recent__avatar" src="/ast/img/oia.png" alt="Diary thumbnail">
                <p class="recent__text">${post.title || "제목 없는 일기"}</p>
            </div>
        `;
        recentListEl.appendChild(item);
    });
}

async function loadRecentPosts() {
    if (!recentListEl) return;
    try {
        const posts = await fetchJson(endpoints.posts);
        renderRecentPosts(posts);
    } catch (error) {
        console.error(error);
        if (error.status === 401) {
            recentListEl.innerHTML = `
                <li class="recent__item recent__item--empty">
                    <span class="recent__date">-</span>
                    <div class="recent__entry">
                        <p class="recent__text recent__text--empty">로그인 후 일기를 확인해 보세요.</p>
                    </div>
                </li>
            `;
        } else {
            recentListEl.innerHTML = `
                <li class="recent__item recent__item--empty">
                    <span class="recent__date">-</span>
                    <div class="recent__entry">
                        <p class="recent__text recent__text--empty">일기를 불러오지 못했습니다.</p>
                    </div>
                </li>
            `;
        }
    }
}

function handleCopyQuote() {
    if (!quoteTextEl) return;
    const quote = quoteTextEl.textContent;
    navigator.clipboard.writeText(quote).then(() => {
        if (noteEl) {
            noteEl.textContent = "복사 완료!";
            setTimeout(() => {
                noteEl.textContent = "복사된 텍스트";
            }, 1600);
        }
    }).catch((error) => {
        console.error("Copy failed", error);
    });
}

function toggleTabs(activeButton, inactiveButton) {
    activeButton?.classList.add("tabs__button--active");
    inactiveButton?.classList.remove("tabs__button--active");
}

function initTabs() {
    tabToday?.addEventListener("click", () => toggleTabs(tabToday, tabDiary));
    tabDiary?.addEventListener("click", () => toggleTabs(tabDiary, tabToday));
}

function init() {
    loadQuote();
    loadRecentPosts();
    quoteCopyBtn?.addEventListener("click", handleCopyQuote);
    initTabs();
}

document.addEventListener("DOMContentLoaded", init);
