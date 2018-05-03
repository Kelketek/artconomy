<template>
  <v-container>
    <v-layout row wrap>
      <v-flex xs12 text-xs-center><h1>See all of the products being offered by those you are watching here!</h1></v-flex>
    </v-layout>
    <store ref="productSearch" class="pt-2" endpoint="/api/sales/v1/who-is-open/" />
  </v-container>
</template>

<script>
  import Store from './Store'
  export default {
    name: 'WhoIsOpen',
    components: {Store}
  }
</script>

<style scoped>

</style>