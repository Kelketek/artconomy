<template>
  <div class="settings-center container">
    <div class="row">
      <div class="main-settings col-12" v-if="$root.user.username">
        <b-tabs v-model="tab">
          <b-tab title="<i class='fa fa-sliders'></i> Options">
            <form class="mt-3">
              <ac-form-container ref="settingsForm" :schema="settingsSchema" :model="settingsModel"
                                 :options="settingsOptions" :success="updateUser"
                                 :url="`/api/profiles/v1/account/${this.user.username}/settings/`"
                                 method="PATCH"
                                 :reset-after="false"
              >
                <b-button type="submit" variant="primary" @click.prevent="$refs.settingsForm.submit">Update</b-button>
                <i v-if="$refs.settingsForm && $refs.settingsForm.saved" class="fa fa-check" style="color: green"></i>
              </ac-form-container>
            </form>
          </b-tab>
          <b-tab title="<i class='fa fa-id-card-o'></i> Credentials">
            <b-tabs pills v-model="credentialsTab">
              <b-tab title="<i class='fa fa-lock'></i> Authentication Details">
                <form class="mt-3">
                  <ac-form-container ref="credentialsForm" :schema="credentialsSchema" :model="credentialsModel"
                                     :options="credentialsOptions" :success="updateCredentials"
                                     :url="`/api/profiles/v1/account/${this.user.username}/credentials/`"
                                     :reset-after="false"
                  >
                    <b-button type="submit" variant="primary" @click.prevent="$refs.credentialsForm.submit">Update</b-button>
                    <i v-if="$refs.credentialsForm && $refs.credentialsForm.saved" class="fa fa-check" style="color: green"></i>
                  </ac-form-container>
                </form>
              </b-tab>
              <b-tab title="<i class='fa fa-shield'></i> Two factor Authentication">
                <ac-setup-two-factor></ac-setup-two-factor>
              </b-tab>
            </b-tabs>
          </b-tab>
          <b-tab title="<i class='fa fa-image'></i> Avatar">
            <div class="text-center mt-3">
              <p>Current Avatar:</p>
              <img class="avatar-preview shadowed mb-3" :src="this.user.avatar_url" />
              <p v-if="user.avatar_url.indexOf('gravatar') > -1">Default avatars provided by <a href="http://en.gravatar.com/">Gravatar</a></p>
            </div>
            <form class="mt-3">
              <legend>Upload a new avatar</legend>
              <ac-form-container ref="avatarForm" :schema="avatarSchema" :model="avatarModel"
                                 :options="avatarOptions" :success="updateAvatar"
                                 :url="`/api/profiles/v1/account/${this.user.username}/avatar/`"
              >
                <b-button type="submit" variant="primary" @click.prevent="$refs.avatarForm.submit">Upload</b-button>
                <i v-if="$refs.avatarForm && $refs.avatarForm.saved" class="fa fa-check" style="color: green"></i>
              </ac-form-container>
            </form>
          </b-tab>
          <b-tab title="<i class='fa fa-money'></i> Payment">
            <b-tabs pills v-model="paymentTab">
              <b-tab title="<i class='fa fa-credit-card'></i> Payment Methods">
                <div class="row mt-3">
                  <div class="col-lg-4 col-md-6 col-12">
                    <ac-card-manager :username="user.username"></ac-card-manager>
                  </div>
                </div>
              </b-tab>
              <b-tab title="<i class='fa fa-usd'></i> Payout Accounts">
                <div class="text-center mt-3">
                  <ac-account-balance :username="user.username"/>
                  <p v-if="user.dwolla_configured">
                    Your Dwolla account has been set up.
                  </p>
                  <p v-else>
                    You must set up a Dwolla account before you can sell on Artconomy. <a :href="user.dwolla_setup_url">Click here</a> to set up your dwolla account.
                  </p>
                </div>
              </b-tab>
            </b-tabs>
          </b-tab>
        </b-tabs>
      </div>
    </div>
  </div>
</template>

<style>
  .avatar-preview {
    border: 1px solid black;
  }
</style>

<script>
  import VueFormGenerator from 'vue-form-generator'
  import AcFormContainer from './ac-form-container'
  import Viewer from '../mixins/viewer'
  import Perms from '../mixins/permissions'
  import { inputMatches, paramHandleMap, ratings, setMetaContent } from '../lib'
  import AcCardManager from './ac-card-manager'
  import AcAccountBalance from './ac-account-balance'
  import AcSetupTwoFactor from './ac-setup-two-factor'

  const TabMap = {
    options: 0,
    credentials: 1,
    avatar: 2,
    payment: 3
  }
  const PaymentTabMap = {
    methods: 0,
    disbursements: 1
  }
  const credentialsTabMap = {
    details: 0,
    'two-factor': 1
  }

  export default {
    name: 'Settings',
    components: {
      AcSetupTwoFactor,
      AcCardManager,
      AcFormContainer,
      AcAccountBalance
    },
    mixins: [Viewer, Perms],
    methods: {
      updateUser () {
        // The arguments pushed to the success function evaluate as true, so we have to make sure none are passed.
        this.$root.$loadUser()
      },
      updateCredentials () {
        this.credentialsModel.current_password = ''
        this.credentialsModel.new_password = ''
        this.credentialsModel.new_password2 = ''
        if (this.user.username !== this.credentialsModel.username) {
          this.$router.replace(
            {
              name: this.$route.name,
              params: Object.assign({}, this.$route.params, {username: this.credentialsModel.username}),
              query: this.$route.query
            }
          )
          this.user.username = this.credentialsModel.username
          this.refreshUser()
          this.refreshUser()
          if (this.is_current) {
            this.$root.$loadUser()
          }
        }
        // Fool form into thinking nothing has changed.
        this.$refs.credentialsForm.oldValue = JSON.parse(JSON.stringify(this.credentialsModel))
        this.$refs.credentialsForm.saved = true
      },
      updateAvatar () {
        this.refreshUser()
        if (this.is_current) {
          this.$root.$loadUser()
        }
      }
    },
    data () {
      return {
        settingsModel: JSON.parse(JSON.stringify(this.$root.user)),
        settingsUpdated: false,
        // Used by Tab mapper
        query: null,
        credentialsModel: {
          username: this.$root.user.username,
          email: this.$root.user.email,
          current_password: '',
          new_password: '',
          new_password2: ''
        },
        settingsSchema: {
          fields: [{
            type: 'checkbox',
            styleClasses: ['vue-checkbox'],
            label: 'Comissions closed?',
            model: 'commissions_closed',
            required: false,
            validator: VueFormGenerator.validators.boolean,
            hint: 'Prevents orders from being placed in your store.'
          }, {
            type: 'input',
            inputType: 'number',
            label: 'Maximum Load',
            model: 'max_load',
            required: false,
            validator: VueFormGenerator.validators.boolean,
            hint: 'Commissions are automatically closed when the total load points of all open orders exceeds this amount.'
          }, {
            type: 'select',
            label: 'Max Content Rating',
            model: 'rating',
            required: false,
            validator: VueFormGenerator.validators.boolean,
            hint: 'By setting this value, you are affirming that the content this rating represents is legal to view in your area and you meet all legal qualifications (such as age) to view it.',
            selectOptions: {
              hideNoneSelectedText: true
            },
            values: ratings
          }, {
            type: 'checkbox',
            styleClasses: ['vue-checkbox'],
            label: 'Safe For Work Mode',
            model: 'sfw_mode',
            required: false,
            validator: VueFormGenerator.validators.boolean,
            hint: 'When enabled, ignores the rating setting and only allows content marked for general audiences to be displayed.'
          }]
        },
        settingsOptions: {
          validateAfterLoad: false,
          validateAfterChanged: true
        },
        credentialsSchema: {
          fields: [{
            type: 'input',
            inputType: 'text',
            label: 'Username',
            model: 'username',
            placeholder: '',
            featured: true,
            required: true,
            hint: 'Warning: This will change all URLs for your profile and all of your submissions. This will affect SEO and bookmarks.',
            validator: VueFormGenerator.validators.string
          }, {
            type: 'input',
            inputType: 'text',
            label: 'Email',
            model: 'email',
            placeholder: 'example@example.com',
            featured: true,
            required: true,
            validator: VueFormGenerator.validators.email
          }, {
            type: 'input',
            inputType: 'password',
            label: 'Current Password',
            model: 'current_password',
            min: 8,
            required: true,
            featured: true,
            validator: VueFormGenerator.validators.string
          }, {
            type: 'input',
            inputType: 'password',
            label: 'New Password',
            model: 'new_password',
            min: 8,
            required: false,
            featured: false,
            validator: VueFormGenerator.validators.string
          }, {
            type: 'input',
            inputType: 'password',
            label: 'New Password (again)',
            model: 'new_password2',
            min: 8,
            required: false,
            featured: false,
            validator: inputMatches('new_password', 'Passwords do not match')
          }]
        },
        credentialsOptions: {
          validateAfterLoad: false,
          validateAfterChanged: true
        },
        avatarModel: {
          avatar: ''
        },
        avatarOptions: {
          validateAfterLoad: false,
          validateAfterChanged: true
        },
        avatarSchema: {
          fields: [{
            type: 'image',
            id: 'avatar',
            label: 'File',
            model: 'avatar',
            required: true
          }]
        }
      }
    },
    created () {
      document.title = `Account settings for ${this.$route.params.username}`
      setMetaContent('description', 'Configure your account settings for Artconomy.')
    },
    computed: {
      tab: paramHandleMap('tabName', TabMap, ['subTabName']),
      paymentTab: paramHandleMap('subTabName', PaymentTabMap),
      credentialsTab: paramHandleMap('subTabName', credentialsTabMap)
    }
  }
</script>