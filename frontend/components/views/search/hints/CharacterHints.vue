<template>
  <v-col>
    <v-row no-gutters>
      <v-col class="text-center" cols="12">
        Try terms like:
        <p>
          <v-chip color="secondary" variant="flat" @click="search('fox')" class="mx-1">fox</v-chip>
          <v-chip color="secondary" variant="flat" @click="search('wolf')" class="mx-1">wolf</v-chip>
          <v-chip color="secondary" variant="flat" @click="search('male')" class="mx-1">male</v-chip>
          <v-chip color="secondary" variant="flat" @click="search('female')" class="mx-1">female</v-chip>
        </p>
      </v-col>
    </v-row>
  </v-col>
</template>

<script setup lang="ts">
import {useForm} from '@/store/forms/hooks.ts'

const searchForm = useForm('search')
const search = (val: string) => searchForm.fields.q.model = val
</script>
