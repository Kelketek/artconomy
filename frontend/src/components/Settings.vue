<template>
  <div class="settings-center container">
    <div class="row">
      <div class="main-settings col-sm-12" v-if="$root.user.username">
        <form>
          <ac-form-container ref="settingsForm" :schema="settingsSchema" :model="settingsModel"
                             :options="settingsOptions" :success="updateUser"
                             :url="`/api/profiles/v1/${this.user.username}/settings/`"
                             method="PATCH"
                             :reset-after="false"
          >
            <b-button type="submit" variant="primary" @click.prevent="$refs.settingsForm.submit">Update</b-button>
            <i v-if="$refs.settingsForm && $refs.settingsForm.saved" class="fa fa-check" style="color: green"></i>
          </ac-form-container>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
  import VueFormGenerator from 'vue-form-generator'
  import AcFormContainer from './ac-form-container'
  import Permissions from '../mixins/permissions'
  import { ratings, setMetaContent } from '../lib'

  export default {
    components: {AcFormContainer},
    mixins: [Permissions],
    methods: {
      updateUser () {
        // The arguments pushed to the success function evaluate as true, so we have to make sure none are passed.
        this.$root.loadUser()
      }
    },
    data () {
      return {
        settingsModel: JSON.parse(JSON.stringify(this.$root.user)),
        settingsUpdated: false,
        credentialsModel: {
          username: '',
          password: '',
          password2: ''
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
        }
      }
    },
    created () {
      document.title = `Account settings for ${this.$route.params.username}`
      setMetaContent('description', 'Configure your account settings for Artconomy.')
    }
  }
</script>