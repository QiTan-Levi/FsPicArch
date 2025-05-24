import { createStore } from 'vuex'

export default createStore({
  state: {
    isLoggedIn: false,
    userId: null,
    userName: null,
    userAvatar: null
  },
  mutations: {
    setLoginState(state, { isLoggedIn, userId, userName, userAvatar }) {
      state.isLoggedIn = isLoggedIn
      state.userId = userId
      state.userName = userName
      state.userAvatar = userAvatar
    }
  },
  actions: {
    initLoginState({ commit }) {
      const userInfo = document.cookie
        .split('; ')
        .find(row => row.startsWith('user-info='))
      
      if (userInfo) {
        const userData = JSON.parse(decodeURIComponent(userInfo.split('=')[1]))
        commit('setLoginState', {
          isLoggedIn: true,
          userId: userData.userId,
          userName: userData.username,
          userAvatar: userData.userAvatar
        })
      } else {
        commit('setLoginState', {
          isLoggedIn: false,
          userId: null,
          userName: null,
          userAvatar: null
        })
      }
    },
    logout({ commit }) {
      // 清除 cookie
      document.cookie = 'user-info=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;'
      document.cookie = 'token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;'
      
      // 重置状态
      commit('setLoginState', {
        isLoggedIn: false,
        userId: null,
        userName: null,
        userAvatar: null
      })
    }
  }
})