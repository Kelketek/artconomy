<template>
  <div class="settings-center container">
    <div class="row">
      <div class="main-settings col-12" v-if="user.username">
        <v-tabs v-model="tab" fixed-tabs>
          <v-tab href="#tab-options">
            <v-icon>build</v-icon>&nbsp;Options
          </v-tab>
          <v-tab href="#tab-credentials">
            <v-icon>lock</v-icon>&nbsp;Credentials
          </v-tab>
          <v-tab href="#tab-avatar">
            <v-icon>person</v-icon>&nbsp;Avatar
          </v-tab>
          <v-tab href="#tab-payment">
            <v-icon>attach_money</v-icon>&nbsp;Payment
          </v-tab>
        </v-tabs>
        <v-tabs-items v-model="tab">
          <v-tab-item id="tab-options">
            <form class="mt-3">
              <ac-form-container ref="settingsForm" :schema="settingsSchema" :model="settingsModel"
                                 :options="settingsOptions" :success="updateUser"
                                 :url="`/api/profiles/v1/account/${this.user.username}/settings/`"
                                 method="PATCH"
                                 :reset-after="false"
              >
                <v-btn type="submit" color="primary" @click.prevent="$refs.settingsForm.submit">Update</v-btn>
                <i v-if="$refs.settingsForm && $refs.settingsForm.saved" class="fa fa-check" style="color: green"></i>
              </ac-form-container>
            </form>
            <div class="pt-2">
              <h2>Blacklist</h2>
              <p>Any submissions which contain content with blacklisted tags will be hidden.</p>
              <ac-tag-display
                  :editable="true"
                  :url="`/api/profiles/v1/account/${this.user.username}/blacklist/`"
                  :callback="updateUser"
                  :tag-list="user.blacklist"
                  :controls="true"
                  :hide-title="true"
              />
            </div>
          </v-tab-item>
          <v-tab-item id="tab-credentials">
            <v-tabs v-model="credentialsTab">
              <v-tab href="#tab-authentication">
                <v-icon>lock_outline</v-icon>&nbsp;Authentication Details
              </v-tab>
              <v-tab href="#tab-two-factor">
                <v-icon>phonelink_lock</v-icon>&nbsp;Two factor Authentication
              </v-tab>
            </v-tabs>
            <v-tabs-items v-model="credentialsTab">
              <v-tab-item id="tab-authentication">
                <form class="mt-3">
                  <ac-form-container ref="credentialsForm" :schema="credentialsSchema" :model="credentialsModel"
                                     :options="credentialsOptions" :success="updateCredentials"
                                     :url="`/api/profiles/v1/account/${this.user.username}/credentials/`"
                                     :reset-after="false"
                  >
                    <v-btn type="submit" color="primary" @click.prevent="$refs.credentialsForm.submit">Update</v-btn>
                    <i v-if="$refs.credentialsForm && $refs.credentialsForm.saved" class="fa fa-check" style="color: green"></i>
                  </ac-form-container>
                </form>
              </v-tab-item>
              <v-tab-item id="tab-two-factor">
                <ac-setup-two-factor />
              </v-tab-item>
            </v-tabs-items>
          </v-tab-item>
          <v-tab-item id="tab-avatar">
            <div class="text-xs-center mt-3">
              <p>Current Avatar:</p>
              <img class="avatar-preview shadowed mb-3" :src="this.user.avatar_url" />
              <p v-if="user.avatar_url.indexOf('gravatar') > -1">Default avatars provided by <a href="http://en.gravatar.com/">Gravatar</a></p>
            </div>
            <form class="mt-3 text-xs-center">
              <h3>Upload a new avatar</h3>
              <ac-form-container ref="avatarForm" :schema="avatarSchema" :model="avatarModel"
                                 :options="avatarOptions" :success="updateAvatar"
                                 :url="`/api/profiles/v1/account/${this.user.username}/avatar/`"
              >
                <v-btn type="submit" variant="primary" @click.prevent="$refs.avatarForm.submit">Upload</v-btn>
                <i v-if="$refs.avatarForm && $refs.avatarForm.saved" class="fa fa-check" style="color: green"></i>
              </ac-form-container>
            </form>
          </v-tab-item>
          <v-tab-item id="tab-payment">
            <v-tabs v-model="paymentTab" fixed-tabs>
              <v-tab href="#tab-purchase">
                <v-icon>credit_card</v-icon>&nbsp;Payment Methods
              </v-tab>
              <v-tab href="#tab-disbursement">
                <v-icon>account_balance_wallet</v-icon>&nbsp;Payout Accounts
              </v-tab>
            </v-tabs>
            <v-tabs-items v-model="paymentTab">
              <v-tab-item id="tab-purchase">
                <div class="row mt-3">
                  <div class="col-lg-4 col-md-6 col-12">
                    <ac-card-manager :username="user.username" />
                  </div>
                </div>
              </v-tab-item>
              <v-tab-item id="tab-disbursement">
                <div class="text-xs-center mt-3">
                  <ac-account-balance :username="user.username"/>
                  <p v-if="user.dwolla_configured">
                    Your payout information has been set up.
                  </p>
                  <v-jumbotron v-else color="grey darken-3">
                    <v-container fill-height>
                      <v-layout align-center>
                        <v-flex>
                          <h3 class="display-3">Add a bank account!</h3>
                          <span class="subheading">Add your account information so that we can send you the money you earn through Artconomy.</span>
                          <v-divider class="my-3" />
                          <v-btn large color="primary" class="mx-0" @click="showNewBank = true">Get Started</v-btn>
                        </v-flex>
                      </v-layout>
                    </v-container>
                  </v-jumbotron>
                  <ac-form-dialog ref="bankForm" :schema="bankSchema" :model="bankModel"
                                  :options="credentialsOptions" :success="addBank"
                                  title="Add Bank"
                                  :url="`/api/sales/v1/account/${this.user.username}/banks/`"
                                  v-model="showNewBank"
                  />
                </div>
              </v-tab-item>
            </v-tabs-items>
          </v-tab-item>
        </v-tabs-items>
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
  import { accountTypes, inputMatches, paramHandleMap, ratings, setMetaContent } from '../lib'
  import AcCardManager from './ac-card-manager'
  import AcAccountBalance from './ac-account-balance'
  import AcSetupTwoFactor from './ac-setup-two-factor'
  import AcTagDisplay from './ac-tag-display'
  import AcFormDialog from './ac-form-dialog'

  export default {
    name: 'Settings',
    components: {
      AcFormDialog,
      AcTagDisplay,
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
      },
      addBank (response) {
        console.log(response)
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
        showNewBank: false,
        settingsSchema: {
          fields: [{
            type: 'v-checkbox',
            styleClasses: ['vue-checkbox'],
            label: 'Comissions closed?',
            model: 'commissions_closed',
            required: false,
            validator: VueFormGenerator.validators.boolean,
            hint: 'Prevents orders from being placed in your store.'
          }, {
            type: 'v-text',
            inputType: 'number',
            label: 'Maximum Load',
            model: 'max_load',
            required: false,
            validator: VueFormGenerator.validators.boolean,
            hint: 'Commissions are automatically closed when the total load points of all open orders exceeds this amount.'
          }, {
            type: 'v-select',
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
            type: 'v-checkbox',
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
            type: 'v-text',
            label: 'Username',
            model: 'username',
            placeholder: '',
            featured: true,
            required: true,
            hint: 'Warning: This will change all URLs for your profile and all of your submissions. This will affect SEO and bookmarks.',
            validator: VueFormGenerator.validators.string
          }, {
            type: 'v-text',
            inputType: 'email',
            label: 'Email',
            model: 'email',
            placeholder: 'example@example.com',
            featured: true,
            required: true,
            validator: VueFormGenerator.validators.email
          }, {
            type: 'v-text',
            inputType: 'password',
            label: 'Current Password',
            model: 'current_password',
            min: 8,
            required: true,
            featured: true,
            validator: VueFormGenerator.validators.string
          }, {
            type: 'v-text',
            inputType: 'password',
            label: 'New Password',
            model: 'new_password',
            min: 8,
            required: false,
            featured: false,
            validator: VueFormGenerator.validators.string
          }, {
            type: 'v-text',
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
        bankModel: {
          first_name: '',
          last_name: '',
          type: '0',
          account_number: '',
          routing_number: ''
        },
        bankSchema: {
          fields: [{
            type: 'v-text',
            label: 'First Name',
            model: 'first_name',
            featured: true,
            validator: VueFormGenerator.validators.required
          }, {
            type: 'v-text',
            label: 'Last Name',
            model: 'last_name',
            featured: true,
            validator: VueFormGenerator.validators.required
          }, {
            type: 'v-select',
            label: 'Account Type',
            model: 'type',
            values: accountTypes,
            selectOptions: {
              hideNoneSelectedText: true
            }
          }, {
            type: 'v-text',
            label: 'Account Number',
            model: 'account_number',
            featured: true,
            validator: VueFormGenerator.validators.required
          }, {
            type: 'v-text',
            label: 'Routing Number',
            model: 'routing_number',
            placeholder: '',
            featured: true,
            validator: VueFormGenerator.validators.required
          }]
        },
        avatarModel: {
          avatar: []
        },
        avatarOptions: {
          validateAfterLoad: false,
          validateAfterChanged: true
        },
        avatarSchema: {
          fields: [{
            type: 'v-file-upload',
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
      window.settings = this
    },
    computed: {
      tab: paramHandleMap('tabName', ['subTabName']),
      paymentTab: paramHandleMap('subTabName', undefined, ['tab-purchase', 'tab-disbursement'], 'tab-purchase'),
      credentialsTab: paramHandleMap('subTabName', undefined, ['tab-authentication', 'tab-two-factor'], 'tab-authentication')
    }
  }
</script>