<template>
  <div class="wrapper">
    <input ref="searchField" v-model="query" class="form-control" @input="runQuery" @keydown.enter.prevent="grabFirst" @keydown.space.prevent="literalTag" :placeholder="schema.placeholder" />
    <div class="mb-2 mt-2">
      <div v-if="value.length === 0">Click a tag to add it, or press enter to select the first one. Press space to create a new tag if the first option doesn't exist or match.</div>
      <div v-else><ac-tag v-for="tag in value" :key="tag" :tag="tag" @click="delTag(tag)"/></div>
    </div>
      <div v-if="response" class="tag-search-results">
        <div style="display:inline-block"
             v-for="tag in response"
             :tag="tag"
             :key="tag"
        >
          <ac-tag
              :tag="tag" @click.native.prevent.capture="addTag(tag)"
          />
        </div>
      </div>
  </div>
</template>

<style scoped>
  .tag-name {
    display: inline-block;
    padding-left: .5rem;
    padding-right: .5rem;
    background-color: #dffffc;
    border-radius: .25rem;
    border: solid 1px black;
    margin-left: .1rem;
    margin-right: .1rem;
    margin-bottom: .1rem;
  }
  .tag-preview:first-child {
    display: inline-block;
    background-color: #ffffff;
    padding: .2rem;
  }
</style>

<script>
  import { abstractField } from 'vue-form-generator'
  import Viewer from '../../mixins/viewer'
  import { artCall } from '../../lib'
  import AcAvatar from '../ac-avatar'
  import AcTag from '../ac-tag'

  export default {
    components: {
      AcTag,
      AcAvatar
    },
    name: 'fieldtagsearch',
    mixins: [ Viewer, abstractField ],
    data () {
      return {
        query: '',
        response: null,
        tags: this.value
      }
    },
    methods: {
      runQuery () {
        artCall(`/api/profiles/v1/search/tag/`, 'GET', {q: this.query, size: 9}, this.populateResponse)
      },
      populateResponse (response) {
        this.response = response
      },
      addTag (tag) {
        if (this.tags.indexOf(tag) === -1) {
          tag = tag.replace(/\s+/g, '')
          if (tag === '') {
            this.query = ''
            this.response = null
            return
          }
          this.tags.push(tag)
          this.$emit('input', this.tags)
          this.query = ''
          this.response = null
        }
      },
      delTag (tag) {
        let index = this.tags.indexOf(tag)
        if (index > -1) {
          this.tags.splice(index, 1)
        }
        this.$emit('input', this.tags)
      },
      literalTag () {
        this.addTag(this.query)
      },
      grabFirst () {
        if (this.query === '') {
          this.$parent.$parent.submit()
        }
        if (this.response && this.response.length) {
          this.addTag(this.response[0])
        }
        if (this.response && !this.response.length) {
          this.addTag(this.query)
        }
      }
    }
  }
</script>