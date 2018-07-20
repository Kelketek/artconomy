<template>
  <div>
    <v-layout row wrap>
      <v-flex xs12 text-xs-center mb-2>
        <v-btn color="primary" @click="showNew = true">Generate Order Token</v-btn>
      </v-flex>
      <v-flex text-xs-center v-if="growing && growing.length" xs12>
        <h3>Tokens</h3>
        <v-divider></v-divider>
      </v-flex>
      <v-flex
          xs12 sm6 md4 lg4
          v-for="token in growing"
          :key="token.id"
          text-xs-center
      >
        <v-card>
          <v-card-text>
            {{token.activation_code}} for {{token.email}}<br />
            Expires on {{formatDateTime(token.expires_on)}} <br />
            <v-btn color="red" @click="deleteToken(token)">Revoke</v-btn>
          </v-card-text>
        </v-card>
      </v-flex>
    </v-layout>
    <v-layout row>
      <v-flex xs12 text-xs-center>
        <div v-if="(growing !== null) && furtherPagination" v-observe-visibility="loadMore"></div>
        <div v-if="fetching && showLoading"><i class="fa fa-spin fa-spinner fa-5x"></i></div>
      </v-flex>
    </v-layout>
    <ac-form-dialog
        v-model="showNew"
        :model="newTokenModel"
        :schema="newTokenSchema"
        :options="newTokenOptions"
        :success="refreshTokens"
        :url="url"
    >
        <v-flex slot="header" text-xs-center>
          <p>Enter an email to send an order token to a customer.</p>
          <strong>Tokens are valid for 24 hours.</strong>
        </v-flex>
    </ac-form-dialog>
  </div>
</template>

<script>
  import {artCall, formatDateTime} from '../lib'
  import VueFormGenerator from 'vue-form-generator'
  import Pagination from '../mixins/paginated'
  import {ObserveVisibility} from 'vue-observe-visibility'
  import AcFormDialog from './ac-form-dialog'

  export default {
    name: 'ac-tokens-list',
    components: {AcFormDialog},
    props: ['endpoint', 'showLoading'],
    directives: {
      ObserveVisibility
    },
    mixins: [Pagination],
    methods: {
      refreshTokens () {
        this.showNew = false
        this.restart()
      },
      deleteToken (token) {
        artCall(`${this.url}${token.id}/`, 'DELETE', undefined, this.spliceToken(token))
      },
      spliceToken (token) {
        let self = this
        return () => {
          let index = self.growing.indexOf(token)
          self.growing.splice(index, 1)
        }
      }
    },
    data () {
      return {
        orderTokens: null,
        formatDateTime,
        growMode: true,
        url: this.endpoint,
        showNew: false,
        newTokenModel: {
          email: ''
        },
        newTokenSchema: {
          fields: [{
            type: 'v-text',
            inputType: 'text',
            label: 'Email',
            model: 'email',
            placeholder: 'example@example.com',
            featured: true,
            required: true,
            validator: VueFormGenerator.validators.email
          }]
        },
        newTokenOptions: {
          validateAfterLoad: false,
          validateAfterChanged: true
        }
      }
    },
    created () {
      this.fetchItems()
    }
  }
</script>

<style scoped>

</style>