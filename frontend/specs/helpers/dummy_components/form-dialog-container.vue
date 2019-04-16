<template>
  <ac-form-dialog v-model="expanded"></ac-form-dialog>
</template>

<script lang="ts">
import Vue from 'vue'
import Component from 'vue-class-component'
import AcFormDialog from '@/components/wrappers/AcFormDialog.vue'

  @Component({
    components: {AcFormDialog},
  })
export default class FormDialogContainer extends Vue {
    public expanded = false
}
</script>

<style scoped>

</style>
