<template>
  <div class="wrapper">
    <input ref="searchField" v-model="query" class="form-control" @input="runQuery" @keyup.enter.capture="grabFirst" :placeholder="schema.placeholder" />
    <div class="mb-2 mt-2">
      <div v-if="userIDs.length === 0">Click a character to add them.</div>
      <div v-else><div class="char-name" v-for="user in users" :key="char.id">({user.username}}) <i class="fa fa-times" @click="delChar(user)"></i></div></div>
    </div>
      <div v-if="response" class="char-search-results">
        <ac-avatar
            v-for="char in response.results"
            v-bind:character="char"
            v-bind:expanded="true"
            v-bind:key="char.id"
            @click.native.prevent.capture="delUser(char)"
        />
      </div>
  </div>
</template>

<style scoped>
  .char-name {
    display: inline-block;
    padding-left: .5rem;
    padding-right: .5rem;
    background-color: #dffffc;
    border-radius: .25rem;
    border: solid 1px black;
    margin-left: .1rem;
    margin-right: .1rem;
  }
  .character-preview:first-child {
    background-color: #dffffc;
  }
</style>

<script>
  import { abstractField } from 'vue-form-generator'
  import Viewer from '../mixins/viewer'
  import AcCharacterPreview from './ac-character-preview'
  import { artCall } from '../lib'
  import AcAvatar from './ac-avatar'

  export default {
    components: {
      AcAvatar
    },
    name: 'fieldCharacterSearch',
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
      delUser (char) {
        if (this.userIDs.indexOf(char.id) === -1) {
          this.characters.push(char)
          this.userIDs.push(char.id)
          this.$emit('input', this.userIDs)
          this.query = ''
          this.response = null
        }
      },
      delChar (char) {
        let index = this.userIDs.indexOf(char.id)
        if (index > -1) {
          this.userIDs.splice(index, 1)
        }
        index = this.characters.indexOf(char)
        if (index > -1) {
          this.characters.splice(index, 1)
        }
      },
      grabFirst (event) {
        console.log(event)
        if (this.response && this.response.results.length) {
          this.delUser(this.response.results[0])
        }
        event.preventDefault()
      }
    },
    created () {
      window.field = this
    }
  }
</script>