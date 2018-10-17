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
          <v-tab href="#tab-portrait">
            <v-icon>portrait</v-icon>&nbsp;Portrait&nbsp;<v-icon>stars</v-icon>
          </v-tab>
          <v-tab href="#tab-landscape">
            <v-icon>landscape</v-icon>&nbsp;Landscape&nbsp;<v-icon>stars</v-icon>
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
                <ac-setup-two-factor :username="username" class="mt-2"/>
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
              <v-tab href="#tab-transactions">
                <v-icon>list</v-icon> Transaction History
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
                <ac-account-balance :username="user.username"/>
              </v-tab-item>
              <v-tab-item id="tab-transactions">
                <ac-transaction-history :endpoint="`/api/sales/v1/account/${user.username}/transactions/`" :username="user.username" />
              </v-tab-item>
            </v-tabs-items>
          </v-tab-item>
          <v-tab-item id="tab-portrait">
            <v-jumbotron v-if="newPortrait" color="grey darken-3">
              <v-container fill-height>
                <v-layout align-center>
                  <v-flex>
                    <h3 class="display-3">Try Artconomy Portrait!</h3>
                    <span class="subheading">Know when your favorite artists are open with Artconomy Portrait</span>
                    <v-divider class="my-3" />
                    <v-btn large color="primary" class="mx-0" :to="{name: 'Upgrade'}">Notify Me!</v-btn>
                  </v-flex>
                </v-layout>
              </v-container>
            </v-jumbotron>
            <v-layout v-else>
              <v-card-text>
                <v-layout row wrap>
                  <v-flex text-xs-center xs12>
                    <v-jumbotron color="grey darken-3">
                      <v-container fill-height>
                        <v-layout align-center>
                          <v-flex>
                            <h3 class="display-3">Welcome to Artconomy Portrait!</h3>
                            <span class="subheading">You are currently receiving emails for your watchlist. If you'd like to get messages via Telegram, click the button below.</span>
                            <v-divider class="my-3" />
                            <v-btn large color="primary" :href="user.telegram_link" class="mx-0" target="_blank"><v-icon>fa-telegram</v-icon>&nbsp;Notify me via Telegram!</v-btn>
                            <p><strong>Note:</strong> Notifications will not be sent more than once for each artist on a given day to prevent spamming.</p>
                          </v-flex>
                        </v-layout>
                      </v-container>
                    </v-jumbotron>
                  </v-flex>
                  <v-flex xs12 text-xs-center class="pt-3">
                    <v-card>
                      <v-card-text v-if="portraitLimited">
                        <p>You are paid through {{formatDate(user.portrait_paid_through)}}.</p>
                      </v-card-text>
                      <v-card-text v-else-if="user.landscape_enabled">
                        You are receiving portrait features as part of your landscape subscription.
                        Your landscape subscription is paid through {{formatDate(user.landscape_paid_through)}}.
                      </v-card-text>
                      <v-card-text>
                        <ac-action
                            color="red" v-if="user.portrait_enabled || user.landscape_enabled" url="/api/sales/v1/cancel-premium/" :success="updateUser"
                            :confirm="true"
                        >
                          <div class="text-left" slot="confirmation-text">Are you sure you wish to cancel your subscription? Note: You will be able to use the extra features until your current term ends.</div>
                          Cancel Subscription
                        </ac-action>
                        <v-btn v-else color="primary" :to="{name: 'Upgrade'}">Restart Subscription</v-btn>
                      </v-card-text>
                    </v-card>
                  </v-flex>
                </v-layout>
              </v-card-text>
            </v-layout>
          </v-tab-item>
          <v-tab-item id="tab-landscape">
            <v-jumbotron v-if="newLandscape" color="grey darken-3">
              <v-container fill-height>
                <v-layout align-center>
                  <v-flex>
                    <h3 class="display-3">Try Artconomy Landscape!</h3>
                    <span class="subheading">Lower your fees for commissions, and be the first to try new features!</span>
                    <v-divider class="my-3" />
                    <v-btn large color="primary" class="mx-0" :to="{name: 'Upgrade'}">Go for it!</v-btn>
                  </v-flex>
                </v-layout>
              </v-container>
            </v-jumbotron>
            <v-layout v-else-if="pricing">
              <v-card-text>
                <v-layout row wrap>
                  <v-flex xs12>
                    <v-jumbotron color="grey darken-3">
                      <v-container fill-height>
                        <v-layout align-center>
                          <v-flex>
                            <h3 class="display-3">Welcome to Artconomy Landscape!</h3>
                            <span class="subheading">
                              Your commission percentage fee is now {{ pricing.landscape_percentage }}%
                              (down from {{pricing.standard_percentage}}%) and your per-sale fee is
                              ${{pricing.landscape_static}} (down from ${{pricing.standard_static}})
                            </span>
                            <br />
                            <span class="subheading">
                              You will also be first to receive previews for new Artconomy Features, and have access to Portrait features.
                            </span>
                          </v-flex>
                        </v-layout>
                      </v-container>
                    </v-jumbotron>
                  </v-flex>
                  <v-flex xs12 text-xs-center class="pt-3">
                    <v-card>
                      <v-card-text>
                        You are paid through {{formatDate(user.landscape_paid_through)}}.
                      </v-card-text>
                      <v-card-text>
                        <ac-action
                            color="red" v-if="user.portrait_enabled || user.landscape_enabled" url="/api/sales/v1/cancel-premium/" :success="updateUser"
                            :confirm="true"
                        >
                          <div class="text-left" slot="confirmation-text">Are you sure you wish to cancel your subscription? Note: You will be able to use the extra features until your current term ends.</div>
                          Cancel Subscription
                        </ac-action>
                        <v-btn v-else color="primary" :to="{name: 'Upgrade'}">Restart Subscription</v-btn>
                      </v-card-text>
                    </v-card>
                  </v-flex>
                </v-layout>
              </v-card-text>
            </v-layout>
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
  import moment from 'moment'
  import VueFormGenerator from 'vue-form-generator'
  import AcFormContainer from './ac-form-container'
  import Viewer from '../mixins/viewer'
  import Perms from '../mixins/permissions'
  import {artCall, formatDate, inputMatches, paramHandleMap, ratings, setMetaContent} from '../lib'
  import AcCardManager from './ac-card-manager'
  import AcAccountBalance from './ac-account-balance'
  import AcSetupTwoFactor from './ac-setup-two-factor'
  import AcTagDisplay from './ac-tag-display'
  import AcFormDialog from './ac-form-dialog'
  import AcTransactionHistory from './ac-transaction-history'
  import AcAction from './ac-action'

  export default {
    name: 'Settings',
    components: {
      AcAction,
      AcTransactionHistory,
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
      loadPricing (response) {
        this.pricing = response
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
          if (this.isCurrent) {
            this.$root.$loadUser()
          }
        }
        // Fool form into thinking nothing has changed.
        this.$refs.credentialsForm.oldValue = JSON.parse(JSON.stringify(this.credentialsModel))
        this.$refs.credentialsForm.resetFieldErrors()
        this.$refs.credentialsForm.saved = true
      },
      updateAvatar () {
        this.refreshUser()
        if (this.isCurrent) {
          this.$root.$loadUser()
        }
      },
      modelFrom (obj) {
        let newObj = {}
        for (let key of Object.keys(obj)) {
          if (key === 'bank_account_status') {
            continue
          }
          newObj[key] = obj[key]
        }
        this.settingsModel = newObj
      }
    },
    data () {
      return {
        settingsModel: {},
        settingsUpdated: false,
        // Used by Tab mapper
        query: null,
        pricing: null,
        formatDate: formatDate,
        credentialsModel: {
          username: this.$root.user.username,
          email: this.$root.user.email,
          current_password: '',
          new_password: '',
          new_password2: ''
        },
        settingsSchema: {
          fields: [{
            type: 'v-checkbox',
            styleClasses: ['vue-checkbox'],
            label: 'Comissions closed',
            model: 'commissions_closed',
            required: false,
            validator: VueFormGenerator.validators.boolean,
            hint: 'Prevents orders from being placed in your store.'
          }, {
            type: 'v-checkbox',
            styleClasses: ['vue-checkbox'],
            label: 'Favorites hidden',
            model: 'favorites_hidden',
            required: false,
            validator: VueFormGenerator.validators.boolean,
            hint: 'If checked, hides your favorites list from public view.'
          }, {
            type: 'v-checkbox',
            styleClasses: ['vue-checkbox'],
            label: 'Taggable',
            model: 'taggable',
            required: false,
            validator: VueFormGenerator.validators.boolean,
            hint: 'If unchecked, prevents others from tagging you as an artist in a submission.'
          }, {
            type: 'v-text',
            inputType: 'number',
            label: 'Maximum Load',
            model: 'max_load',
            required: false,
            validator: VueFormGenerator.validators.boolean,
            hint: 'Commissions are automatically closed when the total load points of all open orders exceeds this amount.'
          }, {
            type: 'v-checkbox',
            styleClasses: ['vue-checkbox'],
            label: 'Auto Withdraw',
            model: 'auto_withdraw',
            required: false,
            validator: VueFormGenerator.validators.boolean,
            hint: 'If checked, automatically sends any money you earn to your bank account. If not set, you will ' +
              'need to visit your payout account settings to withdraw money.'
          }, {
            type: 'v-text',
            multiLine: true,
            label: 'Commission Info',
            model: 'commission_info',
            hint: 'This text is shown on all products and orders as general information commissioners should know, such ' +
            'as terms of service you wish to provide, contact information, or other expectations you wish to set during ' +
            'the commissioning process.'
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
      this.settingsModel = this.modelFrom(this.$root.user)
      if ((this.viewer.username !== this.username) && !this.viewer.is_staff) {
        this.$error({status: 403})
        return
      }
      document.title = `Settings for ${this.$route.params.username}`
      setMetaContent('description', 'Configure your account settings for Artconomy.')
      window.settings = this
      artCall('/api/sales/v1/pricing-info/', 'GET', undefined, this.loadPricing, this.$error)
    },
    watch: {
      '$root.user': function () {
        // Prevent any changes to the user model from causing surprises when updating settings.
        this.settingsModel = this.modelFrom(this.$root.user)
      }
    },
    computed: {
      tab: paramHandleMap('tabName', ['subTabName']),
      paymentTab: paramHandleMap('subTabName', undefined, ['tab-purchase', 'tab-disbursement', 'tab-transactions'], 'tab-purchase'),
      credentialsTab: paramHandleMap('subTabName', undefined, ['tab-authentication', 'tab-two-factor'], 'tab-authentication'),
      newPortrait () {
        return (!this.user.portrait_enabled) && (
          (this.user.portrait_paid_through === null) || (moment(this.user.portrait_paid_through) <= moment.now()))
      },
      newLandscape () {
        return (!this.user.landscape_enabled) && (
          (this.user.landscape_paid_through === null) || (moment(this.user.landscape_paid_through) <= moment.now()))
      },
      portraitLimited () {
        return !this.user.landscape_enabled && this.user.landscape_enabled
      }
    }
  }
</script>