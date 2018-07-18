<template>
  <div class="wrapper">
    <v-text-field
        ref="searchField"
        v-model="query"
        class="form-control"
        @input.native="runQuery"
        @keydown.enter.prevent.native="grabFirst"
        :placeholder="schema.placeholder"
        :error-messages="errors"
    />
    <div class="mb-2 mt-2">
      <div v-if="characterIDs.length === 0">Click a character to add them.</div>
      <div v-else><v-chip close @input="delChar(char)" class="char-name" v-for="char in characters" :key="char.id"><span v-if="char.user.username !== viewer.username">({{char.user.username}}) </span>{{char.name}}</v-chip></div>
    </div>
      <div v-if="response" class="char-search-results">
        <ac-character-preview
            v-for="(char, index) in response.results"
            v-bind:character="char"
            v-bind:expanded="true"
            v-bind:key="char.id"
            @click.native.prevent.capture="addChar(char)"
            xs12 sm4 lg3
            :class="{primary: index === 0}"
        />
      </div>
      <div v-if="query && response && response.results.length === 0" class="error--text">
        <p>No characters could be found by that name. Have you added this character to your profile?</p>
      </div>
  </div>
</template>

<script>
  import { abstractField } from 'vue-form-generator'
  import Viewer from '../../mixins/viewer'
  import materialField from './materialField'
  import AcCharacterPreview from '../ac-character-preview'
  import { artCall } from '../../lib'

  export default {
    components: {AcCharacterPreview},
    name: 'fieldCharacterSearch',
    mixins: [ Viewer, abstractField, materialField ],
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
          `/api/profiles/v1/search/character/`, 'GET', {q: this.query, new_order: this.schema.commission, size: 9, tagging: this.schema.tagging}, this.populateResponse
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