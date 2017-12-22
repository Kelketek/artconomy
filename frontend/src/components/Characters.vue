<template>
  <div class="container">
    <div class="row-centered" v-if="response !== null">
      <ac-character-preview
        v-for="char in response.results"
        v-bind:character="char"
        v-bind:expanded="true"
        v-bind:key="char.id"
      >
      </ac-character-preview>
      <b-pagination-nav
          align="center" :use-router="true" :base-url="baseURL" :link-gen="linkGen"
          v-model="currentPage" :per-page="pageSize" :number-of-pages="totalPages"
      ></b-pagination-nav>
    </div>
    <div class="row" v-else>
      <div class="text-center" style="width:100%"><i class="fa fa-spin fa-spinner fa-5x"></i></div>
    </div>
    <div class="row-centered" v-if="controls">
      <div class="col-sm-12 pt-3 col-md-4 col-centered text-center">
        <div v-if="showNew">
          <form>
            <ac-form-container ref="newCharForm" :schema="newCharSchema" :model="newCharModel"
                                :options="newCharOptions" :success="addCharacter"
                               :url="`/api/profiles/v1/${this.user.username}/characters/`"
            >
              <b-button @click="showNew=false">Cancel</b-button>
              <b-button type="submit" variant="primary" @click.prevent="$refs.newCharForm.submit">Create</b-button>
            </ac-form-container>
          </form>
        </div>
        <b-button v-else variant="primary" size="lg" @click="showNew=true" id="new-char-button">Add a new character</b-button>
      </div>
    </div>
    <div class="m-2"></div>
  </div>
</template>

<script>
  import Perms from '../mixins/permissions'
  import Paginated from '../mixins/paginated'
  import Viewer from '../mixins/viewer'
  import VueFormGenerator from 'vue-form-generator'
  import {artCall} from '../lib'
  import AcFormContainer from './ac-form-container'
  import AcCharacterPreview from './ac-character-preview'

  export default {
    components: {AcFormContainer, AcCharacterPreview},
    name: 'Characters',
    mixins: [Viewer, Perms, Paginated],
    props: ['embedded'],
    data: function () {
      return {
        newCharModel: {
          name: '',
          description: '',
          private: false,
          open_requests: true,
          open_requests_restrictions: ''
        },
        showNew: false,
        newCharSchema: {
          fields: [{
            type: 'input',
            inputType: 'text',
            label: 'Character name',
            model: 'name',
            placeholder: 'My character',
            featured: true,
            required: true,
            validator: VueFormGenerator.validators.string
          }, {
            type: 'input',
            styleClasses: ['vue-checkbox'],
            inputType: 'checkbox',
            label: 'Private Character?',
            model: 'private',
            required: false,
            validator: VueFormGenerator.validators.boolean,
            hint: 'Only shows this character to people you have explicitly shared them to.'
          }]
        },
        newCharOptions: {
          validateAfterLoad: false,
          validateAfterChanged: true
        }
      }
    },
    methods: {
      populateCharacters (response) {
        this.response = response
      },
      addCharacter (response) {
        this.$router.history.push(
          {name: 'Character', params: {user: this.user.username, character: response.name}, query: {editing: true}}
        )
      },
      fetchCharacters (pageNum) {
        let url = `/api/profiles/v1/${this.user.username}/characters/?page=${this.currentPage}`
        artCall(url, 'GET', undefined, this.populateCharacters)
      }
    },
    created () {
      this.fetchCharacters()
    },
    watch: {
      currentPage () {
        this.fetchCharacters()
      }
    }
  }
</script>
