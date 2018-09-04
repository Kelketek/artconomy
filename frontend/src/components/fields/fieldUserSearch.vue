<template>
  <div class="wrapper">
    <v-text-field ref="searchField" :label="schema.label" v-model="query" class="form-control" @input="runQuery" @keydown.enter.prevent.native="grabFirst" :placeholder="schema.placeholder" />
    <div class="mb-2 mt-2">
      <div v-if="userIDs.length === 0">Click a user to add them, or press enter to add the first one.</div>
      <div v-else><v-chip close v-for="user in users" :key="user.id" :user="user" @input="delUser(user)" >{{user.username}}</v-chip></div>
    </div>
      <div v-if="response" class="user-search-results">
        <div style="display:inline-block"
             v-for="(user, index) in response.results"
             :user="user"
             :key="user.id"
        >
          <ac-avatar
              :user="user"
              @click.native.prevent.capture="addUser(user)"
              class="pt-1"
              :class="{primary: index === 0}"
          />
        </div>
      </div>
  </div>
</template>

<script>
  import { abstractField } from 'vue-form-generator'
  import Viewer from '../../mixins/viewer'
  import { artCall, EventBus } from '../../lib'
  import AcAvatar from '../ac-avatar'

  export default {
    components: {
      AcAvatar
    },
    name: 'fieldUserSearch',
    mixins: [ Viewer, abstractField ],
    data () {
      let data = {
        query: '',
        response: null
      }
      if (this.schema.multiple) {
        data.users = []
        data.userIDs = this.value
      } else {
        data.users = []
        data.userIDs = this.value ? [this.value] : []
      }
      if (data.userIDs.length) {
        for (let userID in data.userIDs.length) {
          this.populateUser(userID)
        }
      }
      return data
    },
    watch: {
      value (newVal) {
        if (Array.isArray(newVal) && newVal.length === 0) {
          this.users = []
          this.userIDs = newVal
        }
      }
    },
    created () {
      EventBus.$on('userfield-add-' + this.schema.model, this.addUser)
    },
    destroyed () {
      EventBus.$off('userfield-add-' + this.schema.model, this.addUser)
    },
    methods: {
      runQuery () {
        artCall(`/api/profiles/v1/search/user/`, 'GET', {q: this.query, size: 9, tagging: this.schema.tagging}, this.populateResponse)
      },
      populateResponse (response) {
        this.response = response
      },
      addUser (user) {
        if (this.userIDs.indexOf(user.id) === -1) {
          if (this.schema.multiple) {
            this.users.push(user)
            this.userIDs.push(user.id)
            this.$emit('input', this.userIDs)
            this.value = this.userIDs
          } else {
            this.users = [user]
            this.userIDs = [user.id]
            this.$emit('input', this.userIDs[0])
            this.value = user.id
          }
          this.query = ''
          this.response = null
        }
      },
      delUser (user) {
        let index = this.userIDs.indexOf(user.id)
        if (index > -1) {
          this.userIDs.splice(index, 1)
        }
        index = this.users.indexOf(user)
        if (index > -1) {
          this.users.splice(index, 1)
        }
      },
      grabFirst () {
        if (this.query === '') {
          this.$parent.$parent.submit()
        }
        if (this.response && this.response.results.length) {
          this.addUser(this.response.results[0])
        }
      }
    }
  }
</script>