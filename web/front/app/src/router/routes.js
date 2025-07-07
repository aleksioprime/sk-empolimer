import { isLoggedIn } from "@/middlewares/isLoggedIn";

export const routes = [
  {
    path: "/",
    name: "dashboard",
    component: () => import("@/views/Dashboard.vue"),
    meta: {
      title: 'Главная страница',
      middlewares: [isLoggedIn],
    },
    children: [
      {
        path: "",
        name: "devices",
        component: () => import("@/views/Devices.vue"),
        meta: {
          title: 'Устройства',
        },
      },
      {
        path: "/profile",
        name: "profile",
        component: () => import("@/views/Profile.vue"),
        meta: {
          title: 'Профиль пользователя',
        },
      },
      {
        path: "/users",
        name: "users",
        component: () => import("@/views/Users.vue"),
        meta: {
          title: 'Пользователи',
        },
      },
    ]
  },
  {
    path: "/login",
    name: "login",
    component: () => import("@/views/Login.vue"),
    meta: {
      title: 'Авторизация',
    },
  },
]