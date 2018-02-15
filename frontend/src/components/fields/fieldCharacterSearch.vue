<template>
  <div class="wrapper">
    <input ref="searchField" v-model="query" class="form-control" @input="runQuery" @keydown.enter.prevent="grabFirst" :placeholder="schema.placeholder" />
    <div class="mb-2 mt-2">
      <div v-if="characterIDs.length === 0">Click a character to add them.</div>
      <div v-else><div class="char-name" v-for="char in characters" :key="char.id"><span v-if="char.user.username !== viewer.username">({{char.user.username}}) </span>{{char.name}} <i class="fa fa-times" @click="delChar(char)"></i></div></div>
    </div>
      <div v-if="response" class="char-search-results">
        <ac-character-preview
            v-for="char in response.results"
            v-bind:character="char"
            v-bind:expanded="true"
            v-bind:key="char.id"
            @click.native.prevent.capture="addChar(char)"
        ></ac-character-preview>
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
  import Viewer from '../../mixins/viewer'
  import AcCharacterPreview from '../ac-character-preview'
  import { artCall } from '../../lib'

  export default {
    components: {AcCharacterPreview},
    name: 'fieldCharacterSearch',
    mixins: [ Viewer, abstractField ],
    data () {
      return {
        query: '',
        response: null,
        characters: [],
        characterIDs: this.value
      }
    },
    methods: {
      runQuery () {
        artCall(
          `/api/profiles/v1/search/character/`, 'GET', {q: this.query, new_order: 1, size: 9}, this.populateResponse
        )
      },
      populateResponse (response) {
        this.response = response
      },
      addChar (char) {
        if (this.characterIDs.indexOf(char.id) === -1) {
          this.characters.push(char)
          this.characterIDs.push(char.id)
          this.$emit('input', this.characterIDs)
          this.query = ''
          this.response = null
        }
      },
      delChar (char) {
        let index = this.characterIDs.indexOf(char.id)
        if (index > -1) {
          this.characterIDs.splice(index, 1)
        }
        index = this.characters.indexOf(char)
        if (index > -1) {
          this.characters.splice(index, 1)
        }
      },
      grabFirst () {
        if (this.query === '') {
          this.$parent.$parent.submit()
        }
        if (this.response && this.response.results.length) {
          this.addChar(this.response.results[0])
        }
      }
    }
  }
</script>