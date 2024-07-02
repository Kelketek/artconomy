import {Component, mixins} from 'vue-facing-decorator'
import {FormController} from '@/store/forms/form-controller.ts'
import {User} from '@/store/profiles/types/User.ts'
import Viewer, {useViewer} from '@/mixins/viewer.ts'
import {singleQ} from '@/lib/lib.ts'
import {useForm} from '@/store/forms/hooks.ts'
import {useRoute, useRouter} from 'vue-router'

@Component
export class Auth extends mixins(Viewer) {
  public loginForm = null as unknown as FormController
  public registerForm = null as unknown as FormController
  public forgotForm = null as unknown as FormController

  public sendToProfile() {
    this.$router.push(
      {
        name: 'Profile',
        params: {username: (this.viewer as User).username},
        query: {editing: 'true'},
      },
    )
  }

  public loginHandler(response: User) {
    this.viewerHandler.user.x = response
    if ('next' in this.$route.query) {
      if (singleQ(this.$route.query.next) === '/') {
        this.$router.push({
          name: 'Profile',
          params: {username: response.username},
        })
        return
      }
      this.$router.push(singleQ(this.$route.query.next))
    } else if (this.$route.name === 'Register') {
      this.sendToProfile()
    } else {
      this.$router.push({name: 'Home'})
    }
  }

  public created() {
    this.loginForm = this.$getForm('login', {
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
    this.registerForm = this.$getForm('register', {
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
    this.forgotForm = this.$getForm('forgot', {
      endpoint: '/api/profiles/forgot-password/',
      fields: {
        email: {
          value: '',
          validators: [{name: 'required'}],
        },
      },
    })
  }
}

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
