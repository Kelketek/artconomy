<template>
  <v-app>
    <ac-form-dialog v-model="expanded" ref="dialog"/>
  </v-app>
</template>

<script setup lang="ts">
import AcFormDialog from '@/components/wrappers/AcFormDialog.vue'
import {ref} from 'vue'

const expanded = ref(false)
</script>
