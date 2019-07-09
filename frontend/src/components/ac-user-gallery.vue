<template>
  <v-container v-if="response" grid-list-md>
    <slot name="header" v-if="show && header" />
    <v-layout row wrap>
      <v-flex xs12 text-xs-center v-if="error">
        <p>{{error}}</p>
      </v-flex>
    </v-layout>
    <v-layout row wrap>
      <v-flex xs12 text-xs-center v-if="show">
        <v-pagination v-model="currentPage" :length="totalPages" v-if="totalPages > 1 && !noPagination" :total-visible="totalVisibleByViewport" />
      </v-flex>
      <ac-avatar
          :user="user"
          v-for="(user, key, index) in results"
          :key="key" :id="'user-' + key"
          xs6 sm4 lg2
      />
      <v-flex xs12 text-xs-center v-if="show">
        <v-pagination v-model="currentPage" :length="totalPages" v-if="totalPages > 1 && !noPagination" :total-visible="totalVisibleByViewport" />
      </v-flex>
      <v-flex v-if="noPagination && to && currentPage !== totalPages" xs12 text-xs-center>
        <v-btn color="primary" :to="to">{{seeMoreText}}</v-btn>
      </v-flex>
    </v-layout>
  </v-container>
</template>

<script>
  import Paginated from '../mixins/paginated'
  import AcAvatar from './ac-avatar'
  export default {
    props: ['endpoint', 'header', 'noPagination', 'to', 'seeMoreText'],
    components: {AcAvatar},
    data () {
      return {
        url: this.endpoint
      }
    },
    watch: {
      rating () {
        this.fetchItems()
      },
      endpoint () {
        this.url = this.endpoint
        this.fetchItems()
      }
    },
    name: 'ac-user-gallery',
    mixins: [Paginated],
    computed: {
      show () {
        return this.response !== null && this.nonEmpty
      },
      results () {
        if (this.response === null) {
          return []
        } else {
          return this.response.results
        }
      }
    }
  }
</script>

<style scoped>

</style>
