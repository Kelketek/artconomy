<template>
  <v-container>
    <v-tabs v-model="tab" fixed-tabs>
      <v-tab href="#tab-inbox"><v-icon>mail</v-icon>&nbsp;Inbox</v-tab>
      <v-tab href="#tab-sent"><v-icon>send</v-icon>&nbsp;Sent</v-tab>
    </v-tabs>
    <v-tabs-items v-model="tab">
      <v-tab-item id="tab-inbox">
        <ac-message-list :endpoint="`${url}inbox/`" :username="username" />
      </v-tab-item>
      <v-tab-item id="tab-sent">
        <ac-message-list :endpoint="`${url}sent/`" :username="username" :is-sender="true" />
      </v-tab-item>
    </v-tabs-items>
    <ac-form-dialog ref="newMessageForm" :schema="newMessageSchema" :model="newMessageModel"
                    :options="newMessageOptions" :success="goToMessage"
                    title="New Message"
                    :url="`${url}sent/`"
                    v-model="showNew"
    />
    <ac-add-button text="New Message" v-model="showNew"></ac-add-button>
  </v-container>
</template>

<script>
  import {paramHandleMap} from '../lib'
  import Viewer from '../mixins/viewer'
  import Perms from '../mixins/permissions'
  import AcMessageList from './ac-message-list'
  import AcFormDialog from './ac-form-dialog'
  import VueFormGenerator from 'vue-form-generator'
  import AcAddButton from './ac-add-button'

  export default {
    name: 'Messages',
    components: {AcAddButton, AcFormDialog, AcMessageList},
    mixins: [Viewer, Perms],
    data () {
      return {
        showNew: false,
        newMessageModel: {
          subject: '',
          body: '',
          recipients: []
        },
        newMessageSchema: {
          fields: [{
            type: 'user-search',
            model: 'recipients',
            label: 'Recipients',
            featured: true,
            tagging: true,
            placeholder: 'Search users',
            styleClasses: 'field-input',
            multiple: true
          }, {
            type: 'v-text',
            inputType: 'text',
            label: 'Subject',
            model: 'subject',
            featured: true,
            required: true,
            validator: VueFormGenerator.validators.string
          },
          {
            type: 'v-text',
            label: 'Body',
            model: 'body',
            featured: true,
            multiLine: true,
            required: true,
            validator: VueFormGenerator.validators.string
          }]
        },
        newMessageOptions: {
          validateAfterLoad: false,
          validateAfterChanged: true
        }
      }
    },
    methods: {
      goToMessage (response) {
        this.$router.push({name: 'Message', params: {messageID: response.id, username: response.sender.username}})
      }
    },
    computed: {
      tab: paramHandleMap('tabName', undefined, undefined, 'tab-inbox'),
      url () {
        return `/api/profiles/v1/account/${this.username}/messages/`
      }
    }
  }
</script>

<style scoped>

</style>