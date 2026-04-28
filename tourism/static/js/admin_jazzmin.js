document.addEventListener("DOMContentLoaded", function () {
    const groups = [
        {
            title: "Overview",
            match: ["/admin/", "/admin/dashboard/", "/admin/reports/"],
        },
        {
            title: "Content",
            match: [
                "/admin/tourism/touristplace/",
                "/admin/tourism/templeguide/",
                "/admin/tourism/review/",
                "/admin/tourism/tripplan/",
                "/admin/tourism/chathistory/",
            ],
        },
        {
            title: "Operations",
            match: [
                "/admin/tourism/booking/",
                "/admin/tourism/localservice/",
                "/admin/tourism/notification/",
                "/admin/tourism/favouriteplace/",
            ],
        },
        {
            title: "Access",
            match: ["/admin/auth/user/", "/admin/auth/group/", "/admin/tourism/userprofile/"],
        },
    ];

    const nav = document.querySelector(".main-sidebar .nav-sidebar");
    if (!nav) return;

    const links = Array.from(nav.querySelectorAll("a.nav-link"));
    const created = new Set();

    groups.forEach((group) => {
        const targetLink = links.find((link) => {
            const href = link.getAttribute("href") || "";
            return group.match.some((needle) => href.indexOf(needle) === 0);
        });

        if (!targetLink || created.has(group.title)) return;
        const parent = targetLink.closest(".nav-item");
        if (!parent) return;

        const heading = document.createElement("li");
        heading.className = "nav-item nav-sidebar-heading";
        heading.innerHTML = '<span class="nav-sidebar-heading__label">' + group.title + "</span>";
        nav.insertBefore(heading, parent);
        created.add(group.title);
    });
});
