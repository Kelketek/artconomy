import {useViewer} from '@/mixins/viewer.ts'
import {singleQ} from '@/lib/lib.ts'
import {useForm} from '@/store/forms/hooks.ts'
import {useRoute, useRouter} from 'vue-router'
import {User} from '@/store/profiles/types/main'

export const useAuth = () => {
  const router = useRouter()
  const route = useRoute()
  const {viewerHandler, viewer} = useViewer()
  const loginForm = useForm('login', {
    endpoint: '/api/profiles/login/',
    fields: {
      email: {
        value: '',
        validators: [{name: 'email'}, {name: 'required'}],
      },
      password: {
        value: '',
        validators: [{name: 'required'}],
      },
      token: {value: ''},
      order_claim: {
        value: '',
        omitIf: '',
      },
    },
  })
  const registerForm = useForm('register', {
    endpoint: '/api/profiles/register/',
    fields: {
      username: {
        value: '',
        validators: [{
          name: 'username',
          async: true,
        }],
      },
      email: {
        value: '',
        validators: [
          {
            name: 'email',
            async: true,
          },
        ],
      },
      password: {
        value: '',
        validators: [{name: 'required'}, {
          name: 'password',
          async: true,
        }],
      },
      recaptcha: {
        value: '',
        validators: [{name: 'required'}],
      },
      artist_mode: {value: false},
      registration_code: {value: ''},
      mail: {value: true},
      order_claim: {
        value: '',
        omitIf: '',
      },
    },
  })
  const forgotForm = useForm('forgot', {
    endpoint: '/api/profiles/forgot-password/',
    fields: {
      email: {
        value: '',
        validators: [{name: 'required'}],
      },
    },
  })

  const loginHandler = (response: User) => {
    viewerHandler.user.x = response
    if ('next' in route.query) {
      if (singleQ(route.query.next) === '/') {
        return router.push({
          name: 'Profile',
          params: {username: response.username},
        })
      }
      return router.push(singleQ(route.query.next))
    } else if (route.name === 'Register') {
      return sendToProfile()
    }
    return router.push({name: 'Home'})
  }

  const sendToProfile = () => {
    return router.push(
      {
        name: 'Profile',
        params: {username: viewer.value.username},
        query: {editing: 'true'},
      },
    )
  }

  return {loginForm, registerForm, forgotForm, loginHandler, sendToProfile}
}
