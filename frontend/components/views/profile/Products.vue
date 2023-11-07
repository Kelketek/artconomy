<template>
  <v-container>
    <ac-subjective-product-list :username="username"/>
  </v-container>
</template>

<script lang="ts">
import Subjective from '../../../mixins/subjective'
import {Component, mixins, toNative} from 'vue-facing-decorator'
import AcProductList from '@/components/views/store/AcProductList.vue'
import AcSubjectiveProductList from '@/components/views/store/AcSubjectiveProductList.vue'

@Component({
  components: {
    AcSubjectiveProductList,
    AcProductList,
  },
})
class Products extends mixins(Subjective) {
}

export default toNative(Products)
</script>
