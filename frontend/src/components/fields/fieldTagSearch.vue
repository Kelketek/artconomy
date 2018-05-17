<template>
  <div class="wrapper">
    <v-text-field ref="searchField" v-model="query" class="form-control" @input="runQuery" @keydown.enter.prevent.native="grabFirst" @keydown.space.prevent.native="literalTag" @blur="blurHandler" :placeholder="schema.placeholder" />
    <div class="mb-2 mt-2">
      <div v-if="value.length === 0">Click a tag to add it, or press enter to select the first one. Press space to create a new tag if the first option doesn't exist or match.</div>
      <div v-else><v-chip close v-for="tag in value" :key="tag" :tag="tag" @input="delTag(tag)">{{tag}}</v-chip></div>
    </div>
      <div v-if="response" class="tag-search-results">
        <div style="display:inline-block"
             v-for="(tag, index) in response"
             :tag="tag"
             :key="tag"
        >
          <ac-tag
              :tag="tag" @click.native.prevent.capture="addTag(tag)"
              :class="{primary: index === 0}"
          />
        </div>
      </div>
  </div>
</template>

<script>
  import { abstractField } from 'vue-form-generator'
  import Viewer from '../../mixins/viewer'
  import {artCall} from '../../lib'
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
      defaultSelect () {
        if (this.query) {
          this.literalTag()
        }
      },
      blurHandler () {
        setTimeout(this.defaultSelect, 250)
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