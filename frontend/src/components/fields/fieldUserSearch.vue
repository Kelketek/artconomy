<template>
  <div class="wrapper">
    <input ref="searchField" v-model="query" class="form-control" @input="runQuery" @keydown.enter.prevent="grabFirst" :placeholder="schema.placeholder" />
    <div class="mb-2 mt-2">
      <div v-if="userIDs.length === 0">Click a user to add them.</div>
      <div v-else><div class="user-name" v-for="user in users" :key="user.id">{{user.username}} <i class="fa fa-times" @click="delUser(user)"></i></div></div>
    </div>
      <div v-if="response" class="user-search-results">
        <div style="display:inline-block"
             v-for="user in response.results"
             :user="user"
             :key="user.id"
        >
          <ac-avatar
              :user="user"
              @click.native.prevent.capture="addUser(user)"
          />
        </div>
      </div>
  </div>
</template>

<style scoped>
  .user-name {
    display: inline-block;
    padding-left: .5rem;
    padding-right: .5rem;
    background-color: #dffffc;
    border-radius: .25rem;
    border: solid 1px black;
    margin-left: .1rem;
    margin-right: .1rem;
  }
  .user-preview:first-child {
    background-color: #dffffc;
  }
</style>

<script>
  import { abstractField } from 'vue-form-generator'
  import Viewer from '../../mixins/viewer'
  import { artCall } from '../../lib'
  import AcAvatar from '../ac-avatar'

  export default {
    components: {
      AcAvatar
    },
    name: 'fieldUserSearch',
    mixins: [ Viewer, abstractField ],
    data () {
      return {
        query: '',
        response: null,
        users: [],
        userIDs: this.value
      }
    },
    methods: {
      runQuery () {
        artCall(`/api/profiles/v1/search/user/`, 'GET', {q: this.query, size: 9}, this.populateResponse)
      },
      populateResponse (response) {
        this.response = response
      },
      addUser (user) {
        if (this.userIDs.indexOf(user.id) === -1) {
          this.users.push(user)
          this.userIDs.push(user.id)
          this.$emit('input', this.userIDs)
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