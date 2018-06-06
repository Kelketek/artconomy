<template>
    <div>
      <v-icon
          v-for="i in [1, 2, 3, 4, 5]" v-if="response !== null || !url" :key="i" @mouseover="hoverStars = i"
          @mouseout="hoverStars = null" @click="stars = i" :small="small"
      >{{icon(i)}}</v-icon>
      <div class="error-text" v-html="errors.stars || ''"></div>
      <v-text-field
       v-model="comments"
       :counter="1000"
       :multi-line="true"
       label="Rating Comments"
       v-if="editable"
       :error-messages="errors.comments"
      />
      <v-btn color="purple" @click="submit" v-if="editable">Submit Rating</v-btn>
    </div>
</template>

<style scoped>
  .error-text {
    color: red
  }
</style>

<script>
  import {artCall, EventBus} from '../lib'

  export default {
    props: {
      'url': {},
      'value': {},
      'small': {},
      'commentsText': {}
    },
    data () {
      return {
        response: null,
        setStars: null,
        hoverStars: null,
        errors: {},
        comments: this.commentsText
      }
    },
    methods: {
      loadRating (response) {
        this.setStars = response.stars
        this.comments = response.comments
        this.response = response
        if (this.setStars && this.url) {
          EventBus.$emit('rating-submitted')
        }
      },
      loadError (response) {
        this.errors = response.responseJSON
      },
      icon (number) {
        if (this.stars === null) {
          return 'star_outline'
        }
        if ((this.stars < number) && (this.stars > (number - 1))) {
          return 'star_half'
        } else if (number <= this.stars) {
          return 'star'
        } else {
          return 'star_outline'
        }
      },
      submit () {
        artCall(this.url, 'POST', {stars: this.setStars, comments: this.comments}, this.loadRating, this.loadError)
      }
    },
    created () {
      if (this.url) {
        artCall(this.url, 'GET', undefined, this.loadRating)
      }
    },
    computed: {
      stars: {
        get () {
          if (!this.editable) {
            // Special case this, since if value is null it would pass through otherwise.
            return this.value || 0
          }
          return this.value || this.hoverStars || this.setStars
        },
        set (value) {
          if (!this.editable) {
            return
          }
          this.setStars = value
        }
      },
      editable () {
        return Boolean(this.url)
      }
    }
  }
</script>