<template>
  <v-container>
    <v-layout row wrap class="mt-5">
      <v-flex xs12 md6 offset-md3 text-xs-center>
        <form class="mt-3" v-if="validated === true">
          <p>Reset password for {{username}}</p>
          <ac-form-container ref="resetForm" :schema="resetSchema" :model="resetModel"
                             :options="resetOptions" :success="postReset"
                             :url="`/api/profiles/v1/forgot-password/perform-reset/${this.username}/${this.resetToken}/`"
                             :reset-after="false"
          >
            <v-btn type="submit" color="primary" @click.prevent="$refs.resetForm.submit">Update</v-btn>
          </ac-form-container>
        </form>
        <p v-else-if="validated === false">
          The password token you've provided has expired.
          <router-link :to="{name: 'Login', params: {tabName: 'forgot'}}">Please request a new password reset link.</router-link>
        </p>
        <i class="fa fa-spin fa-spinner fa-5x" v-else></i>
      </v-flex>
    </v-layout>
  </v-container>
</template>

<script>
  import {artCall, inputMatches} from '../lib'
  import VueFormGenerator from 'vue-form-generator'
  import AcFormContainer from './ac-form-container'
  import Perms from '../mixins/permissions'

  export default {
    name: 'PasswordReset',
    components: {AcFormContainer},
    mixins: [Perms],
    props: ['username', 'resetToken'],
    data () {
      return {
        validated: null,
        resetModel: {
          new_password: '',
          new_password2: ''
        },
        resetSchema: {
          fields: [{
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
        resetOptions: {
          validateAfterLoad: false,
          validateAfterChanged: true
        }
      }
    },
    methods: {
      markValid () {
        this.validated = true
      },
      markFailed () {
        this.validated = false
      },
      postReset () {
        delete this.$root.userCache[this.username]
        this.$root.$loadUser(true)
      }
    },
    created () {
      artCall(
        `/api/profiles/v1/forgot-password/token-check/${this.username}/${this.resetToken}/`,
        'GET', undefined, this.markValid, this.markFailed
      )
    }
  }
</script>

<style scoped>

</style>