<template>
  <v-container>
    <ac-subjective-product-list :username="username"/>
  </v-container>
</template>

<script lang="ts">
import Subjective from '../../../mixins/subjective'
import Component, {mixins} from 'vue-class-component'
import AcProductList from '@/components/views/store/AcProductList.vue'
import {ListController} from '@/store/lists/controller'
import Product from '@/types/Product'
import AcSubjectiveProductList from '@/components/views/store/AcSubjectiveProductList.vue'
  @Component({
    components: {AcSubjectiveProductList, AcProductList},
  })
export default class Products extends mixins(Subjective) {
}
</script>
