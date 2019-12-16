<template>
  <v-col>Collection</v-col>
</template>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import Subjective from '@/mixins/subjective'

  @Component
export default class Collection extends mixins(Subjective) {

}
</script>
